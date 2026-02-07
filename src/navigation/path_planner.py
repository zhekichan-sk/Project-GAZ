"""
Планировщик пути.
"""

import math
from dataclasses import dataclass
from typing import List, Optional
from src.common.types import Point
from src.common.geometry import distance
from src.mapping.occupancy_grid import OccupancyGrid
from .astar import AStar


@dataclass
class PathPlanningResult:
    """Результат планирования пути."""
    path: List[Point]
    length: float
    found: bool


class PathPlanner:
    """Планировщик пути с использованием A*."""
    
    def __init__(self, grid: OccupancyGrid, robot_radius: float):
        """
        Args:
            grid: карта занятости
            robot_radius: радиус робота
        """
        self.grid = grid
        self.robot_radius = robot_radius
        self.astar = AStar(grid, robot_radius)
    
    def plan(self, start: Point, goal: Point) -> PathPlanningResult:
        """
        Планирует путь от старта до цели.
        
        Args:
            start: начальная точка
            goal: целевая точка
            
        Returns:
            PathPlanningResult с путем и информацией
        """
        path = self.astar.find_path(start, goal)
        
        if path is None:
            return PathPlanningResult(
                path=[],
                length=0.0,
                found=False
            )
        
        length = self.get_path_length(path)
        
        return PathPlanningResult(
            path=path,
            length=length,
            found=True
        )
    
    def smooth_path(self, path: List[Point]) -> List[Point]:
        """
        Сглаживает путь (опционально).
        
        Args:
            path: исходный путь
            
        Returns:
            Сглаженный путь
        """
        if len(path) < 3:
            return path
        
        smoothed = [path[0]]
        
        i = 0
        while i < len(path) - 1:
            # Пытаемся пропустить промежуточные точки
            j = len(path) - 1
            while j > i + 1:
                # Проверяем, можно ли пройти напрямую от path[i] до path[j]
                if self._is_line_clear(path[i], path[j]):
                    smoothed.append(path[j])
                    i = j
                    break
                j -= 1
            else:
                # Не можем пропустить, добавляем следующую точку
                smoothed.append(path[i + 1])
                i += 1
        
        return smoothed
    
    def _is_line_clear(self, start: Point, end: Point) -> bool:
        """
        Проверяет, свободна ли прямая линия между двумя точками.
        
        Args:
            start: начальная точка
            end: конечная точка
            
        Returns:
            True если линия свободна
        """
        # Получаем ячейки вдоль линии
        cells = self.grid.get_cells_along_ray(start, end)
        
        # Проверяем, что все ячейки свободны
        for i, j in cells:
            if self.grid.get_cell(i, j) >= 0.5:
                return False
        
        return True
    
    def is_goal_reachable(self, goal: Point) -> bool:
        """
        Проверяет, достижима ли цель.
        
        Args:
            goal: целевая точка
            
        Returns:
            True если цель достижима
        """
        goal_i, goal_j = self.grid.world_to_grid(goal)
        return self.astar.is_valid_cell(goal_i, goal_j)
    
    def get_path_length(self, path: List[Point]) -> float:
        """
        Вычисляет длину пути.
        
        Args:
            path: список точек пути
            
        Returns:
            Длина пути
        """
        if len(path) < 2:
            return 0.0
        
        total_length = 0.0
        for i in range(len(path) - 1):
            total_length += distance(path[i], path[i + 1])
        
        return total_length

