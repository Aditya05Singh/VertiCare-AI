from dataclasses import dataclass, field, asdict
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

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


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

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class QualitySummary:
    """Technical quality indicators for the computer-vision tracking sequence."""
    total_frames: int
    valid_frames: int
    valid_ratio: float
    face_detected_ratio: float
    is_sufficient: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


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

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class NystagmusKinematicFeatures:
    """
    Kinematic oscillatory movement parameters derived from temporal eye coordinates.
    Notice: Descriptive kinematic feature observations only.
    Not a clinical diagnosis of nystagmus.
    """
    dominant_frequency_hz: float
    oscillation_amplitude: float
    slow_phase_velocity_mean: float
    fast_phase_velocity_peak: float
    jerk_asymmetry_ratio: float
    dominant_axis: str  # "HORIZONTAL", "VERTICAL", or "INDETERMINATE"
    pattern_type: str    # "JERK_LIKE", "PENDULAR_LIKE", or "PHYSIOLOGICAL_FIXATION"
    observation_summary: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class VideoMetadata:
    """Technical metadata for an analyzed video stream or file."""
    file_path: Optional[str] = None
    width: int = 0
    height: int = 0
    fps: float = 0.0
    total_frames: int = 0
    duration_sec: float = 0.0
    codec: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)



@dataclass
class CVAnalysisResult:
    """Complete result packet from the computer-vision eye tracking pipeline."""
    status: str
    quality: QualitySummary
    features: MovementFeatures
    observation: Dict[str, Any] = field(default_factory=dict)
    session_id: Optional[str] = None
    video_metadata: Optional[VideoMetadata] = None
    nystagmus_analysis: Optional[Dict[str, Any]] = None
    warnings: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
