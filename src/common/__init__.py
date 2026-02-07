"""
Общие утилиты и типы для проекта симулятора робота.
"""

from .types import (
    Point,
    Pose,
    RobotState,
    SimulationMode,
    ObstacleType,
    DEFAULT_FPS,
    DEFAULT_ROBOT_RADIUS,
    DEFAULT_LIDAR_RANGE,
)
from .geometry import (
    distance,
    angle_between,
    normalize_angle,
    rotate_point,
    line_intersection,
    point_in_polygon,
    ray_segment_intersection,
)
from .config_loader import (
    load_environment_config,
    load_robot_config,
    validate_config,
)

__all__ = [
    # Types
    "Point",
    "Pose",
    "RobotState",
    "SimulationMode",
    "ObstacleType",
    # Constants
    "DEFAULT_FPS",
    "DEFAULT_ROBOT_RADIUS",
    "DEFAULT_LIDAR_RANGE",
    # Geometry functions
    "distance",
    "angle_between",
    "normalize_angle",
    "rotate_point",
    "line_intersection",
    "point_in_polygon",
    "ray_segment_intersection",
    # Config loader
    "load_environment_config",
    "load_robot_config",
    "validate_config",
]

