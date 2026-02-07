"""
Построитель карты занятости.
"""

import numpy as np
from typing import TYPE_CHECKING
from src.common.types import Point

if TYPE_CHECKING:
    from .occupancy_grid import OccupancyGrid
    from src.simulation.lidar import LidarScan

# Константы для байесовского обновления
LOG_ODDS_FREE = -0.4  # Свободная ячейка
LOG_ODDS_OCCUPIED = 0.85  # Занятая ячейка
LOG_ODDS_PRIOR = 0.0  # Начальное значение
LOG_ODDS_MIN = -5.0
LOG_ODDS_MAX = 5.0


class Mapper:
    """Построитель карты занятости из данных лидара."""
    
    def __init__(self, grid: 'OccupancyGrid', max_range: float = 300.0):
        """
        Args:
            grid: карта занятости для обновления
            max_range: максимальная дальность лидара
        """
        self.grid = grid
        self.max_range = max_range
    
    def update_from_scan(self, scan: 'LidarScan') -> None:
        """
        Обновляет карту на основе скана лидара.
        
        Args:
            scan: результаты сканирования лидара
        """
        robot_point = Point(scan.robot_pose.x, scan.robot_pose.y)
        
        for i, point in enumerate(scan.points):
            if i >= len(scan.distances):
                continue
            
            distance = scan.distances[i]
            max_range = getattr(scan, 'max_range', self.max_range)
            
            # Пропускаем лучи с максимальной дальностью (не попали в препятствие)
            # Если расстояние близко к max_range, значит луч не попал в препятствие
            if abs(distance - max_range) < 1.0:
                continue
            
            # Получаем ячейки вдоль луча
            cells = self.grid.get_cells_along_ray(robot_point, point)
            
            if not cells:
                continue
            
            # Обновляем свободные ячейки (все кроме последней)
            for cell_i, cell_j in cells[:-1]:
                self.grid.update_cell(cell_i, cell_j, LOG_ODDS_FREE)
            
            # Обновляем конечную ячейку (занятая)
            if cells:
                end_i, end_j = cells[-1]
                self.grid.update_cell(end_i, end_j, LOG_ODDS_OCCUPIED)
    
    def get_completion_percentage(self) -> float:
        """
        Вычисляет процент исследованной карты.
        
        Returns:
            Процент исследованной карты [0.0, 100.0]
        """
        # Считаем ячейки, которые не являются неизвестными (0.5)
        known_cells = np.sum(np.abs(self.grid.grid - 0.5) > 0.1)
        total_cells = self.grid.width * self.grid.height
        
        if total_cells == 0:
            return 0.0
        
        return (known_cells / total_cells) * 100.0
    
    def reset(self) -> None:
        """Сбрасывает карту к начальному состоянию."""
        self.grid.grid.fill(0.5)
        self.grid.log_odds.fill(LOG_ODDS_PRIOR)

