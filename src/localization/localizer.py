"""
Модуль локализации робота на известной карте.
"""

import math
from dataclasses import dataclass
from src.common.types import Pose, Point
from src.common.geometry import distance
from src.simulation.lidar import LidarScan
from src.mapping.occupancy_grid import OccupancyGrid
from .scan_matcher import ScanMatcher


@dataclass
class LocalizationResult:
    """Результат локализации."""
    pose: Pose
    confidence: float  # Уверенность [0.0, 1.0]
    error: float = 0.0  # Отклонение от реальной позиции (если известна)


class Localizer:
    """Модуль локализации робота на известной карте."""
    
    def __init__(self, grid: OccupancyGrid, scan_matcher: ScanMatcher = None):
        """
        Args:
            grid: карта занятости
            scan_matcher: сопоставитель сканов (создается автоматически если None)
        """
        self.grid = grid
        self.scan_matcher = scan_matcher if scan_matcher else ScanMatcher(grid)
    
    def localize(self, scan: LidarScan, odometry_pose: Pose) -> LocalizationResult:
        """
        Локализует робота используя одометрию как начальную оценку.
        
        Args:
            scan: скан лидара
            odometry_pose: поза по одометрии
            
        Returns:
            LocalizationResult с оцененной позой и уверенностью
        """
        # Используем одометрию как начальную оценку
        # Уточняем позицию через scan matching
        search_radius = 20.0  # Радиус поиска в единицах
        angular_range = math.radians(30)  # Диапазон углов ±30 градусов
        
        best_pose, confidence = self.scan_matcher.search_best_pose(
            scan, odometry_pose, search_radius, angular_range
        )
        
        return LocalizationResult(
            pose=best_pose,
            confidence=confidence,
            error=0.0  # Будет вычислено если известна реальная позиция
        )
    
    def global_localization(self, scan: LidarScan) -> LocalizationResult:
        """
        Глобальная локализация без начальной оценки (медленнее).
        
        Args:
            scan: скан лидара
            
        Returns:
            LocalizationResult с оцененной позой
        """
        # Поиск по всей карте (упрощенный - по сетке)
        best_pose = Pose(0, 0, 0)
        best_score = 0.0
        
        # Поиск по сетке карты
        step = 50  # Шаг поиска в единицах
        angle_step = math.radians(45)  # Шаг по углу
        
        for i in range(0, self.grid.height, max(1, int(step / self.grid.resolution))):
            for j in range(0, self.grid.width, max(1, int(step / self.grid.resolution))):
                world_point = self.grid.grid_to_world(i, j)
                
                for angle in range(0, 360, 45):
                    test_pose = Pose(
                        world_point.x,
                        world_point.y,
                        math.radians(angle)
                    )
                    
                    score = self.scan_matcher.compute_score(scan, test_pose)
                    
                    if score > best_score:
                        best_score = score
                        best_pose = test_pose
        
        confidence = min(1.0, best_score)
        
        return LocalizationResult(
            pose=best_pose,
            confidence=confidence,
            error=0.0
        )
    
    def get_position_error(self, estimated: Pose, actual: Pose) -> float:
        """
        Вычисляет ошибку позиции.
        
        Args:
            estimated: оцененная позиция
            actual: реальная позиция
            
        Returns:
            Ошибка в единицах
        """
        pos_error = distance(Point(estimated.x, estimated.y), Point(actual.x, actual.y))
        angle_error = abs(estimated.theta - actual.theta)
        # Нормализуем угол
        while angle_error > math.pi:
            angle_error -= 2 * math.pi
        angle_error = abs(angle_error)
        
        # Комбинированная ошибка (позиция + небольшой вклад угла)
        return pos_error + angle_error * 10.0

