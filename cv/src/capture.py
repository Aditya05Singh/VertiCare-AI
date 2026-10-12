"""
cv/src/capture.py

Video capture, format normalization, video file processing,
and synthetic frame/video generation utilities for eye tracking screening.
"""

import os
from pathlib import Path
from typing import Optional, Generator, Tuple, Any, Dict, Union, List
import cv2
import numpy as np
from cv.src.schemas import VideoMetadata


# Supported video extensions
SUPPORTED_VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".webm", ".mkv"}
MAX_ALLOWED_FILE_SIZE_BYTES = 150 * 1024 * 1024  # 150 MB safety limit
MAX_PROCESSING_FRAMES = 1800                     # 60 seconds at 30 fps limit


class VideoProcessingError(Exception):
    """Base exception for computer vision video processing errors."""
    pass


class UnsupportedFormatError(VideoProcessingError):
    """Raised when an uploaded video file has an unsupported container or format."""
    pass


class EmptyVideoError(VideoProcessingError):
    """Raised when a video file has 0 bytes or contains 0 readable frames."""
    pass


class CorruptedVideoError(VideoProcessingError):
    """Raised when a video file header or frame stream is corrupted and unreadable."""
    pass


def validate_frame(frame: Any) -> bool:
    """Validate that input frame is a non-empty 3-channel numpy array."""
    if frame is None or not isinstance(frame, np.ndarray):
        return False
    if frame.size == 0:
        return False
    if len(frame.shape) != 3 or frame.shape[2] != 3:
        return False
    return True


def normalize_frame_format(
    frame: np.ndarray,
    target_width: int = 640,
    target_height: int = 480
) -> Optional[np.ndarray]:
    """Convert and resize frame to standard RGB representation for landmark tracking."""
    if not validate_frame(frame):
        return None

    try:
        h, w = frame.shape[:2]
        if w != target_width or h != target_height:
            resized = cv2.resize(frame, (target_width, target_height), interpolation=cv2.INTER_AREA)
        else:
            resized = frame

        # Convert to RGB if BGR
        rgb_frame = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        return rgb_frame
    except Exception:
        return None


class VideoFileProcessor:
    """
    Handles robust video file validation, metadata inspection, and frame stream extraction
    with strict processing limits and guaranteed OpenCV resource cleanup.
    """

    @staticmethod
    def inspect_and_validate(file_path: Union[str, Path]) -> VideoMetadata:
        """
        Inspect video file integrity, format, dimensions, duration, and frame count.
        Raises descriptive VideoProcessingError subclasses upon failure.
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Video file not found at: {path}")

        # Check file extension
        suffix = path.suffix.lower()
        if suffix not in SUPPORTED_VIDEO_EXTENSIONS:
            raise UnsupportedFormatError(
                f"Unsupported video format '{suffix}'. Allowed formats: {sorted(list(SUPPORTED_VIDEO_EXTENSIONS))}"
            )

        # Check file size
        file_size = path.stat().st_size
        if file_size == 0:
            raise EmptyVideoError(f"Video file is empty (0 bytes): {path.name}")

        if file_size > MAX_ALLOWED_FILE_SIZE_BYTES:
            raise VideoProcessingError(
                f"Video file size ({round(file_size / (1024 * 1024), 2)} MB) exceeds limit of 150 MB."
            )

        # Attempt to open with OpenCV VideoCapture
        cap = cv2.VideoCapture(str(path))
        try:
            if not cap.isOpened():
                raise CorruptedVideoError(f"OpenCV could not open video container: {path.name}")

            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = float(cap.get(cv2.CAP_PROP_FPS))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            # Normalize missing or anomalous FPS
            if fps <= 0.0 or not np.isfinite(fps) or fps > 240.0:
                fps = 30.0

            # Verify that at least one frame is decodeable
            ret, first_frame = cap.read()
            if not ret or first_frame is None or first_frame.size == 0:
                raise CorruptedVideoError(f"Video container contains no readable frames: {path.name}")

            actual_h, actual_w = first_frame.shape[:2]
            if width <= 0 or height <= 0:
                width, height = actual_w, actual_h

            # If total_frames was 0 or unreadable from container metadata, count first frame
            if total_frames <= 0:
                total_frames = max(1, total_frames)

            duration_sec = total_frames / fps if fps > 0 else 0.0

            return VideoMetadata(
                file_path=str(path),
                width=width,
                height=height,
                fps=round(fps, 2),
                total_frames=total_frames,
                duration_sec=round(duration_sec, 2),
                codec=path.suffix.lstrip(".").upper()
            )
        finally:
            cap.release()

    @staticmethod
    def extract_frames(
        file_path: Union[str, Path],
        max_frames: int = MAX_PROCESSING_FRAMES,
        max_duration_sec: float = 60.0
    ) -> Generator[Tuple[int, float, np.ndarray], None, None]:
        """
        Safely generator-yields (frame_index, timestamp_sec, frame_bgr) from video file.
        Guarantees OpenCV VideoCapture cleanup when generator is closed or exhausted.
        """
        metadata = VideoFileProcessor.inspect_and_validate(file_path)
        fps = metadata.fps if metadata.fps > 0 else 30.0

        cap = cv2.VideoCapture(str(file_path))
        frame_idx = 0

        try:
            while cap.isOpened() and frame_idx < max_frames:
                ret, frame = cap.read()
                if not ret or frame is None:
                    break

                timestamp = frame_idx / fps
                if timestamp > max_duration_sec:
                    break

                yield (frame_idx, timestamp, frame)
                frame_idx += 1
        finally:
            cap.release()


class SyntheticFrameGenerator:
    """
    Generates synthetic frames, eye signals, and test video files for automated testing.
    """

    @staticmethod
    def generate_blank_frame(width: int = 640, height: int = 480) -> np.ndarray:
        return np.zeros((height, width, 3), dtype=np.uint8)

    @staticmethod
    def generate_synthetic_trajectory(
        duration_sec: float = 5.0,
        fps: float = 30.0,
        freq_hz: float = 2.0,
        amplitude: float = 0.08
    ) -> Generator[Tuple[float, float, float], None, None]:
        """Generate (timestamp, x, y) points mimicking horizontal periodic eye oscillation."""
        total_frames = int(duration_sec * fps)
        for i in range(total_frames):
            t = i / fps
            x = 0.5 + amplitude * np.sin(2 * np.pi * freq_hz * t)
            y = 0.5 + 0.01 * np.cos(2 * np.pi * freq_hz * t)
            yield (t, float(x), float(y))

    @staticmethod
    def render_synthetic_eye_frame(
        width: int = 320,
        height: int = 240,
        pupil_x_norm: float = 0.5,
        pupil_y_norm: float = 0.5,
        pupil_radius: int = 16,
        iris_radius: int = 34,
        is_blinking: bool = False
    ) -> np.ndarray:
        """
        Renders a realistic synthetic close-up eye region with sclera, iris, pupil, and eyelids.
        """
        img = np.full((height, width, 3), (220, 225, 230), dtype=np.uint8)  # Skin tone
        center_x = width // 2
        center_y = height // 2

        if is_blinking:
            # Closed eye line
            cv2.ellipse(img, (center_x, center_y), (width // 3, 2), 0, 0, 360, (140, 140, 150), -1)
            return img

        # Sclera (eye white)
        sclera_w = width // 3
        sclera_h = height // 4
        cv2.ellipse(img, (center_x, center_y), (sclera_w, sclera_h), 0, 0, 360, (250, 250, 252), -1)

        # Iris position
        px = int(center_x + (pupil_x_norm - 0.5) * (sclera_w * 1.2))
        py = int(center_y + (pupil_y_norm - 0.5) * (sclera_h * 1.2))

        # Iris (blue/brown)
        cv2.circle(img, (px, py), iris_radius, (160, 110, 60), -1)

        # Pupil (black disk)
        cv2.circle(img, (px, py), pupil_radius, (20, 20, 20), -1)

        # Corneal light reflection
        cv2.circle(img, (px - 5, py - 5), 4, (255, 255, 255), -1)

        # Eyelids
        cv2.ellipse(img, (center_x, center_y - sclera_h), (sclera_w + 10, 15), 0, 0, 180, (190, 180, 185), -1)
        cv2.ellipse(img, (center_x, center_y + sclera_h), (sclera_w + 10, 15), 0, 180, 360, (190, 180, 185), -1)

        return img

    @staticmethod
    def create_synthetic_test_video(
        output_path: Union[str, Path],
        duration_sec: float = 2.0,
        fps: float = 30.0,
        freq_hz: float = 2.5,
        width: int = 320,
        height: int = 240,
        pattern: str = "horizontal_nystagmus"
    ) -> Path:
        """
        Creates and writes a real, valid video file with OpenCV VideoWriter
        containing periodic eye oscillation for end-to-end integration tests.
        """
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(str(out_p), fourcc, fps, (width, height))

        total_frames = int(duration_sec * fps)
        for i in range(total_frames):
            t = i / fps
            if pattern == "normal":
                x_norm = 0.5 + 0.012 * np.sin(0.4 * np.pi * t)
                y_norm = 0.5 + 0.006 * np.cos(0.3 * np.pi * t)
            elif pattern == "vertical_nystagmus":
                x_norm = 0.5 + 0.010 * np.cos(0.5 * np.pi * t)
                y_norm = 0.5 + 0.12 * np.sin(2.0 * np.pi * freq_hz * t)
            else:  # horizontal_nystagmus
                x_norm = 0.5 + 0.15 * np.sin(2.0 * np.pi * freq_hz * t)
                y_norm = 0.5 + 0.02 * np.cos(2.0 * np.pi * freq_hz * t)

            blink = (i % 60 == 0 and i > 0)
            frame = SyntheticFrameGenerator.render_synthetic_eye_frame(
                width=width, height=height, pupil_x_norm=float(x_norm), pupil_y_norm=float(y_norm), is_blinking=blink
            )
            writer.write(frame)

        writer.release()
        return out_p
