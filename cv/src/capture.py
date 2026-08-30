from typing import Optional, Generator, Tuple, Any
import cv2
import numpy as np


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


class SyntheticFrameGenerator:
    """
    Generates synthetic frames and test signals for automated unit tests without requiring a physical camera.
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
