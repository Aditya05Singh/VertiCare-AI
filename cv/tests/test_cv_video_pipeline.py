"""
cv/tests/test_cv_video_pipeline.py

Comprehensive independent test suite for CV video ingestion,
RANSAC pupil tracking, error handling, resource cleanup, and schema validation.
"""

import os
import tempfile
import time
from pathlib import Path
import pytest
import numpy as np
import cv2

from cv.src.capture import (
    VideoFileProcessor,
    SyntheticFrameGenerator,
    VideoProcessingError,
    UnsupportedFormatError,
    EmptyVideoError,
    CorruptedVideoError,
)
from cv.src.pipeline import CVPipeline
from cv.src.landmarks import MediaPipeLandmarkAdapter
from cv.src.schemas import CVAnalysisResult, VideoMetadata


def test_cv_dependencies_and_imports():
    """1. Verify critical CV dependencies and imports are available."""
    import cv2
    import numpy as np
    import mediapipe
    from cv.src.pipeline import CVPipeline

    assert cv2.__version__ is not None
    assert np.__version__ is not None
    pipeline = CVPipeline()
    assert pipeline is not None


def test_cv_detector_initialization():
    """2. Verify landmark adapter and detector initialize gracefully without crashing."""
    adapter = MediaPipeLandmarkAdapter()
    assert adapter is not None
    # Feed empty frame to verify safe handling
    res = adapter.extract_landmarks(None)
    assert res is None


def test_cv_valid_video_processing_end_to_end(tmp_path):
    """
    3. Genuine End-to-End Video Inference:
    Generates a real valid MP4 video containing periodic eye motion,
    runs CVPipeline.process_video_file, and verifies extracted kinematics.
    """
    video_file = tmp_path / "valid_eye_movement.mp4"
    SyntheticFrameGenerator.create_synthetic_test_video(
        output_path=video_file,
        duration_sec=1.5,
        fps=30.0,
        freq_hz=2.0,
        width=320,
        height=240
    )
    assert video_file.exists()
    assert video_file.stat().st_size > 0

    pipeline = CVPipeline(session_id="integration-valid-session")
    result: CVAnalysisResult = pipeline.process_video_file(video_file)

    assert result.session_id == "integration-valid-session"
    assert result.status == "COMPLETED"
    assert result.quality.is_sufficient is True
    assert result.quality.valid_frames >= 20
    assert result.video_metadata is not None
    assert result.video_metadata.fps == 30.0
    assert result.video_metadata.total_frames >= 40
    assert result.features.horizontal_velocity_mean >= 0.0
    assert result.features.direction_changes_h >= 0
    assert result.nystagmus_analysis is not None
    assert "Does not establish medical diagnosis" in result.nystagmus_analysis["clinical_disclaimer"]


def test_cv_corrupted_video_file_handling(tmp_path):
    """4. Verify corrupted video files (random garbage bytes) are rejected gracefully."""
    corrupted_file = tmp_path / "corrupted_video.mp4"
    corrupted_file.write_bytes(b"\x00\x01\x02\x03CORRUPTED_NOT_A_REAL_VIDEO_STREAM\xFF\xFE")

    pipeline = CVPipeline(session_id="corrupted-session")
    result = pipeline.process_video_file(corrupted_file)

    assert result.status == "FAILED"
    assert result.quality.is_sufficient is False
    assert len(result.warnings) > 0
    assert "failed" in result.observation["message"].lower() or "error" in result.observation["status"].lower()


def test_cv_empty_video_file_handling(tmp_path):
    """5a. Verify empty video file (0 bytes) raises/handles EmptyVideoError."""
    empty_file = tmp_path / "empty_video.mp4"
    empty_file.touch()
    assert empty_file.stat().st_size == 0

    pipeline = CVPipeline(session_id="empty-session")
    result = pipeline.process_video_file(empty_file)

    assert result.status == "FAILED"
    assert "empty" in result.warnings[0].lower()


def test_cv_unsupported_format_handling(tmp_path):
    """4b. Verify unsupported container extensions are rejected."""
    unsupported_file = tmp_path / "eye_recording.txt"
    unsupported_file.write_text("not a video")

    pipeline = CVPipeline(session_id="unsupported-session")
    result = pipeline.process_video_file(unsupported_file)

    assert result.status == "FAILED"
    assert "unsupported" in result.warnings[0].lower()


def test_cv_insufficient_frames_handling(tmp_path):
    """5b. Verify video with insufficient frames (< 10) flags INSUFFICIENT_QUALITY."""
    short_file = tmp_path / "short_video.mp4"
    SyntheticFrameGenerator.create_synthetic_test_video(
        output_path=short_file,
        duration_sec=0.15,  # Only ~4 frames at 30 fps
        fps=30.0,
        width=320,
        height=240
    )

    pipeline = CVPipeline(session_id="short-session")
    result = pipeline.process_video_file(short_file)

    assert result.status == "INSUFFICIENT_QUALITY"
    assert result.quality.is_sufficient is False
    assert result.observation["status"] == "INSUFFICIENT_QUALITY"


def test_cv_failed_detection_blank_video(tmp_path):
    """6. Verify video with solid black frames handles detection failure cleanly."""
    blank_file = tmp_path / "blank_video.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(blank_file), fourcc, 30.0, (320, 240))
    for _ in range(30):
        writer.write(np.zeros((240, 320, 3), dtype=np.uint8))
    writer.release()

    pipeline = CVPipeline(session_id="blank-session")
    result = pipeline.process_video_file(blank_file)

    assert result.status == "INSUFFICIENT_QUALITY"
    assert result.quality.valid_frames == 0
    assert result.quality.valid_ratio == 0.0


def test_cv_output_schema_validation(tmp_path):
    """7. Output schema validation: verify all required attributes are present and typed."""
    video_file = tmp_path / "schema_test.mp4"
    SyntheticFrameGenerator.create_synthetic_test_video(video_file, duration_sec=1.0, fps=30.0)

    pipeline = CVPipeline(session_id="schema-check")
    result = pipeline.process_video_file(video_file)

    assert isinstance(result.status, str)
    assert isinstance(result.quality.valid_ratio, float)
    assert isinstance(result.quality.total_frames, int)
    assert isinstance(result.features.horizontal_velocity_mean, float)
    assert isinstance(result.features.direction_changes_h, int)
    assert isinstance(result.warnings, list)
    assert isinstance(result.limitations, list)
    assert len(result.limitations) > 0


def test_cv_resource_cleanup_allows_file_deletion(tmp_path):
    """8. Resource cleanup: verify video file handles are released so file can be safely unlinked."""
    video_file = tmp_path / "cleanup_test.mp4"
    SyntheticFrameGenerator.create_synthetic_test_video(video_file, duration_sec=1.0, fps=30.0)

    pipeline = CVPipeline()
    result = pipeline.process_video_file(video_file)
    assert result.status == "COMPLETED"

    # Must be able to delete file immediately without PermissionError or file lock
    video_file.unlink()
    assert not video_file.exists()


def test_cv_repeated_inference_and_performance(tmp_path):
    """9. Repeated inference and performance: runs 3 video evaluations in sequence."""
    video_file = tmp_path / "perf_test.mp4"
    SyntheticFrameGenerator.create_synthetic_test_video(video_file, duration_sec=1.0, fps=30.0)

    pipeline = CVPipeline(session_id="perf-session")

    start_time = time.time()
    for i in range(3):
        res = pipeline.process_video_file(video_file)
        assert res.status == "COMPLETED"
        assert res.quality.valid_frames > 0
    elapsed = time.time() - start_time

    # Processing 3 1-second videos should take < 5 seconds
    assert elapsed < 5.0

