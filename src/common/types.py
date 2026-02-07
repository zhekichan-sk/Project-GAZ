"""
Общие типы данных и константы для проекта.
"""

from dataclasses import dataclass
from enum import Enum
from typing import NamedTuple


class Point(NamedTuple):
    """Точка в двумерном пространстве."""
    x: float
    y: float


@dataclass
class Pose:
    """Позиция и ориентация робота."""
    x: float
    y: float
    theta: float  # Ориентация в радианах


class RobotState(Enum):
    """Состояния робота."""
    IDLE = "idle"
    MOVING = "moving"
    MAPPING = "mapping"
    LOCALIZING = "localizing"
    NAVIGATING = "navigating"


class SimulationMode(Enum):
    """Режимы симуляции."""
    MAPPING = "mapping"
    LOCALIZATION = "localization"
    NAVIGATION = "navigation"


class ObstacleType(Enum):
    """Типы препятствий."""
    WALL = "wall"
    RECTANGLE = "rectangle"
    POLYGON = "polygon"
    CIRCLE = "circle"


# Константы
DEFAULT_FPS = 60
DEFAULT_ROBOT_RADIUS = 15.0
DEFAULT_LIDAR_RANGE = 300.0

