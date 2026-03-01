"""
Сопоставление сканов с картой (Scan Matching).
"""

import math
import numpy as np
from typing import Tuple
from src.common.types import Pose, Point
from src.simulation.lidar import LidarScan
from src.mapping.occupancy_grid import OccupancyGrid


class ScanMatcher:
    """Сопоставление скана лидара с картой занятости."""
    
    def __init__(self, grid: OccupancyGrid):
        """
        Args:
            grid: карта занятости
        """
        self.grid = grid
    
    def compute_score(self, scan: LidarScan, pose: Pose, step: int = 10) -> float:
        """
        Вычисляет оценку совпадения скана с картой для данной позы.
        
        Args:
            scan: скан лидара
            pose: поза робота для проверки
            step: шаг выборки лучей (1=все, 10=каждый 10-й) для ускорения
            
        Returns:
            Оценка совпадения (высокий score = хорошее совпадение)
        """
        score = 0.0
        valid_points = 0
        
        for idx in range(0, len(scan.points), step):
            point = scan.points[idx]
            if idx >= len(scan.distances):
                continue
            
            # Преобразуем точку скана в глобальные координаты с учетом новой позы
            # Угол луча относительно робота
            if hasattr(scan, 'angles') and idx < len(scan.angles):
                ray_angle = scan.angles[idx]
            else:
                # Если углы недоступны, вычисляем из точки
                ray_angle = math.atan2(point.y - scan.robot_pose.y, point.x - scan.robot_pose.x) - scan.robot_pose.theta
            dist = scan.distances[idx]
            
            # Глобальный угол
            global_angle = pose.theta + ray_angle
            
            # Глобальные координаты точки
            global_x = pose.x + dist * math.cos(global_angle)
            global_y = pose.y + dist * math.sin(global_angle)
            global_point = Point(global_x, global_y)
            
            # Получаем ячейку на карте
            cell_i, cell_j = self.grid.world_to_grid(global_point)
            
            if self.grid.is_in_bounds(cell_i, cell_j):
                # Вероятность занятости в этой ячейке
                occupancy = self.grid.get_cell(cell_i, cell_j)
                # Высокая вероятность занятости = хорошее совпадение
                score += occupancy
                valid_points += 1
        
        # Нормализуем по количеству валидных точек
        if valid_points > 0:
            return score / valid_points
        return 0.0
    
    def search_best_pose(self, scan: LidarScan, initial_pose: Pose,
                        search_radius: float, angular_range: float) -> Tuple[Pose, float]:
        """
        Ищет лучшую позицию в окрестности initial_pose.
        
        Args:
            scan: скан лидара
            initial_pose: начальная оценка позы
            search_radius: радиус поиска в единицах
            angular_range: диапазон углов для поиска в радианах
            
        Returns:
            (best_pose, confidence) - лучшая поза и уверенность
        """
        best_pose = initial_pose
        best_score = self.compute_score(scan, initial_pose, step=10)
        
        # Параметры поиска (уменьшено для производительности)
        position_step = search_radius / 3.0  # 7 шагов по позиции
        angle_step = angular_range / 5.0  # 11 шагов по углу
        
        # Поиск по позиции
        for dx in np.arange(-search_radius, search_radius + position_step, position_step):
            for dy in np.arange(-search_radius, search_radius + position_step, position_step):
                # Поиск по углу
                for dtheta in np.arange(-angular_range, angular_range + angle_step, angle_step):
                    test_pose = Pose(
                        initial_pose.x + dx,
                        initial_pose.y + dy,
                        initial_pose.theta + dtheta
                    )
                    
                    score = self.compute_score(scan, test_pose, step=10)
                    
                    if score > best_score:
                        best_score = score
                        best_pose = test_pose
        
        # Confidence - нормализованный score
        confidence = min(1.0, best_score)
        
        return best_pose, confidence

