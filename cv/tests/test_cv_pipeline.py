import pytest
import numpy as np
from cv.src.pipeline import CVPipeline
from cv.src.schemas import TemporalSample
from cv.src.capture import SyntheticFrameGenerator


def test_cv_pipeline_synthetic_samples():
    pipeline = CVPipeline(session_id="test-session-123")

    # Ingest 30 synthetic periodic samples
    for t, x, y in SyntheticFrameGenerator.generate_synthetic_trajectory(duration_sec=1.0, fps=30.0):
        pipeline.add_sample(
            TemporalSample(
                timestamp=t,
                left_x=x - 0.2,
                left_y=y,
                right_x=x + 0.2,
                right_y=y,
                left_ear=0.32,
                right_ear=0.32,
                valid=True
            )
        )

    result = pipeline.analyze()
    assert result.status == "COMPLETED"
    assert result.quality.is_sufficient is True
    assert result.quality.valid_frames == 30
    assert result.features.horizontal_amplitude > 0.05
    assert result.features.direction_changes_h > 0
    assert result.observation["status"] == "FEATURES_AVAILABLE"


def test_cv_pipeline_insufficient_quality():
    pipeline = CVPipeline(session_id="poor-quality-session")

    # Ingest 30 mostly invalid frames (face not found / bad lighting)
    for i in range(30):
        pipeline.add_sample(
            TemporalSample(
                timestamp=i * 0.033,
                left_x=0.0,
                left_y=0.0,
                right_x=0.0,
                right_y=0.0,
                valid=(i < 5)  # only 5 valid
            )
        )

    result = pipeline.analyze()
    assert result.status == "INSUFFICIENT_QUALITY"
    assert result.quality.is_sufficient is False
    assert result.observation["status"] == "INSUFFICIENT_QUALITY"
    assert "technical threshold" in result.observation["message"]

