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
from .ant_colony import AntColony


@dataclass
class PathPlanningResult:
    """Результат планирования пути."""
    path: List[Point]
    length: float
    found: bool


class PathPlanner:
    """Планировщик пути (муравьиные колонии / A*)."""
    
    def __init__(self, grid: OccupancyGrid, robot_radius: float, use_aco: bool = True):
        """
        Args:
            grid: карта занятости
            robot_radius: радиус робота
            use_aco: True — муравьиные колонии, False — A*
        """
        self.grid = grid
        self.robot_radius = robot_radius
        self.use_aco = use_aco
        self.astar = AStar(grid, robot_radius)
        self.ant_colony = AntColony(grid, robot_radius)
    
    def plan(self, start: Point, goal: Point) -> PathPlanningResult:
        """
        Планирует путь от старта до цели.
        
        Args:
            start: начальная точка
            goal: целевая точка
            
        Returns:
            PathPlanningResult с путем и информацией
        """
        if self.use_aco:
            path = self.ant_colony.find_path(start, goal)
            if path is None:
                path = self.astar.find_path(start, goal)
        else:
            path = self.astar.find_path(start, goal)
        
        if path is None or len(path) < 2:
            return PathPlanningResult(
                path=[],
                length=0.0,
                found=False
            )
        
        # Сглаживание: прямая линия когда возможно, повороты только для обхода препятствий
        smoothed = self.smooth_path(path)
        length = self.get_path_length(smoothed)
        
        return PathPlanningResult(
            path=smoothed,
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
        Проверяет, свободна ли прямая линия между двумя точками (учитывая радиус робота).
        
        Returns:
            True если линия свободна, можно идти напрямую
        """
        grid = self.astar.inflated_grid  # сетка с учётом радиуса робота
        cells = grid.get_cells_along_ray(start, end)
        for i, j in cells:
            if grid.get_cell(i, j) > 0.5:  # занято
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
        checker = self.ant_colony if self.use_aco else self.astar
        return checker.is_valid_cell(goal_i, goal_j)
    
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

