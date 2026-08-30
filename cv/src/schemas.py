from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class NormalizedEyePosition:
    """Normalized 2D eye positions and aspect ratios within facial reference frame."""
    left_x: float
    left_y: float
    right_x: float
    right_y: float
    left_ear: float = 0.3
    right_ear: float = 0.3
    inter_ocular_distance: float = 1.0


@dataclass
class TemporalSample:
    """Single time-stamped eye coordinate measurement."""
    timestamp: float
    left_x: float
    left_y: float
    right_x: float
    right_y: float
    left_ear: float = 0.3
    right_ear: float = 0.3
    valid: bool = True


@dataclass
class QualitySummary:
    """Technical quality indicators for the computer-vision tracking sequence."""
    total_frames: int
    valid_frames: int
    valid_ratio: float
    face_detected_ratio: float
    is_sufficient: bool


@dataclass
class MovementFeatures:
    """Computational eye-movement features extracted from the temporal signal."""
    horizontal_amplitude: float
    vertical_amplitude: float
    horizontal_velocity_mean: float
    vertical_velocity_mean: float
    horizontal_velocity_max: float
    vertical_velocity_max: float
    direction_changes_h: int
    direction_changes_v: int
    blink_count: int
    blink_rate_per_min: float


@dataclass
class CVAnalysisResult:
    """Complete result packet from the computer-vision eye tracking pipeline."""
    status: str
    quality: QualitySummary
    features: MovementFeatures
    observation: Dict[str, Any] = field(default_factory=dict)
    session_id: Optional[str] = None

