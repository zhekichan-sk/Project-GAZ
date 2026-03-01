"""
Среда с препятствиями для симуляции.
"""

import math
from typing import List, Optional
from src.common.types import Point
from src.common.geometry import ray_segment_intersection, distance
from src.simulation.obstacles import Obstacles, RectangleObstacle


class Environment:
    """Среда с препятствиями."""
    
    # Отступы для вычисления области сетки
    MARGIN_LEFT = 50
    MARGIN_TOP = 50
    MARGIN_RIGHT = 220  # панель справа (кнопки, мини-карта)
    MARGIN_BOTTOM = 130
    GRID_SIZE = 100
    
    def __init__(self, width: int = 1500, height: int = 1200, obstacles: List = None):
        """
        Args:
            width: ширина среды
            height: высота среды
            obstacles: список препятствий
        """
        self.width = width
        self.height = height
        self.obstacles = obstacles if obstacles else Obstacles()
        self.background_color = (255, 255, 255)
        self.boundary_obstacles: List = []  # Жёлтые стены по границам сетки
        self._update_grid_bounds()
    
    def _update_grid_bounds(self) -> None:
        """Обновляет границы сетки и создаёт жёлтые стены по краям."""
        self.grid_left = self.MARGIN_LEFT
        self.grid_top = self.MARGIN_TOP
        self.grid_right = self.width - self.MARGIN_RIGHT
        self.grid_bottom = self.height - self.MARGIN_BOTTOM
        # Выравниваем по размеру ячейки
        grid_w = self.grid_right - self.grid_left
        grid_h = self.grid_bottom - self.grid_top
        cols = max(1, grid_w // self.GRID_SIZE)
        rows = max(1, grid_h // self.GRID_SIZE)
        self.grid_right = self.grid_left + cols * self.GRID_SIZE
        self.grid_bottom = self.grid_top + rows * self.GRID_SIZE
        
        # Жёлтые стены по границам сетки (лидар не выходит за пределы)
        wall_thick = 5
        self.boundary_obstacles = [
            # Левая стена
            RectangleObstacle(
                self.grid_left - wall_thick / 2,
                (self.grid_top + self.grid_bottom) / 2,
                wall_thick, self.grid_bottom - self.grid_top + wall_thick * 2, 0
            ),
            # Правая стена
            RectangleObstacle(
                self.grid_right + wall_thick / 2,
                (self.grid_top + self.grid_bottom) / 2,
                wall_thick, self.grid_bottom - self.grid_top + wall_thick * 2, 0
            ),
            # Верхняя стена
            RectangleObstacle(
                (self.grid_left + self.grid_right) / 2,
                self.grid_top - wall_thick / 2,
                self.grid_right - self.grid_left + wall_thick * 2, wall_thick, 0
            ),
            # Нижняя стена
            RectangleObstacle(
                (self.grid_left + self.grid_right) / 2,
                self.grid_bottom + wall_thick / 2,
                self.grid_right - self.grid_left + wall_thick * 2, wall_thick, 0
            ),
        ]
    
    def is_valid_position(self, point: Point, radius: float) -> bool:
        """
        Проверяет, является ли позиция валидной (нет коллизий).
        
        Args:
            point: точка для проверки
            radius: радиус объекта
            
        Returns:
            True если позиция валидна, False если есть коллизия
        """
        # Проверка границ сетки (робот должен ходить только по сетке)
        # Центр робота должен быть не ближе radius от границ сетки
        if point.x < self.grid_left + radius or point.x > self.grid_right - radius:
            return False
        if point.y < self.grid_top + radius or point.y > self.grid_bottom - radius:
            return False
        
        # Проверка коллизий с препятствиями
        for obstacle in self.obstacles.get_placed_obstacles():
            if isinstance(obstacle, RectangleObstacle):
                # Проверяем расстояние от точки до препятствия
                corners = obstacle.get_corners()
                if len(corners) >= 3:
                    # Проверяем, находится ли точка внутри препятствия
                    if obstacle.contains_point(point.x, point.y):
                        return False
                    
                    # Проверяем расстояние до границ препятствия
                    min_dist = float('inf')
                    for i in range(len(corners)):
                        p1 = Point(corners[i][0], corners[i][1])
                        p2 = Point(corners[(i + 1) % len(corners)][0], 
                                  corners[(i + 1) % len(corners)][1])
                        
                        # Расстояние от точки до отрезка
                        seg_dist = self._point_to_segment_distance(point, p1, p2)
                        min_dist = min(min_dist, seg_dist)
                    
                    if min_dist < radius:
                        return False
        
        return True
    
    def _point_to_segment_distance(self, point: Point, seg_start: Point, seg_end: Point) -> float:
        """Вычисляет расстояние от точки до отрезка."""
        # Вектор отрезка
        dx = seg_end.x - seg_start.x
        dy = seg_end.y - seg_start.y
        
        # Если отрезок - точка
        if dx == 0 and dy == 0:
            return distance(point, seg_start)
        
        # Параметр t для проекции точки на отрезок
        t = max(0, min(1, ((point.x - seg_start.x) * dx + (point.y - seg_start.y) * dy) / (dx * dx + dy * dy)))
        
        # Ближайшая точка на отрезке
        proj_x = seg_start.x + t * dx
        proj_y = seg_start.y + t * dy
        
        return distance(point, Point(proj_x, proj_y))
    
    def raycast(self, origin: Point, angle: float, max_dist: float) -> float:
        """
        Трассировка луча до препятствия.
        Луч ограничен границами сетки (лидар не выходит за пределы клетки).
        
        Args:
            origin: начало луча
            angle: угол луча в радианах
            max_dist: максимальное расстояние
            
        Returns:
            Расстояние до препятствия или max_dist если препятствия нет
        """
        min_distance = max_dist
        
        # Границы сетки (лидар не выходит за пределы)
        # Левая граница
        if math.cos(angle) < 0:
            t = (self.grid_left - origin.x) / math.cos(angle)
            if t > 0:
                y = origin.y + t * math.sin(angle)
                if self.grid_top <= y <= self.grid_bottom:
                    min_distance = min(min_distance, t)
        
        # Правая граница
        if math.cos(angle) > 0:
            t = (self.grid_right - origin.x) / math.cos(angle)
            if t > 0:
                y = origin.y + t * math.sin(angle)
                if self.grid_top <= y <= self.grid_bottom:
                    min_distance = min(min_distance, t)
        
        # Верхняя граница
        if math.sin(angle) < 0:
            t = (self.grid_top - origin.y) / math.sin(angle)
            if t > 0:
                x = origin.x + t * math.cos(angle)
                if self.grid_left <= x <= self.grid_right:
                    min_distance = min(min_distance, t)
        
        # Нижняя граница
        if math.sin(angle) > 0:
            t = (self.grid_bottom - origin.y) / math.sin(angle)
            if t > 0:
                x = origin.x + t * math.cos(angle)
                if self.grid_left <= x <= self.grid_right:
                    min_distance = min(min_distance, t)
        
        # Проверка препятствий (размещённые + границы сетки)
        all_obstacles = list(self.obstacles.get_placed_obstacles()) + self.boundary_obstacles
        for obstacle in all_obstacles:
            if isinstance(obstacle, RectangleObstacle):
                corners = obstacle.get_corners()
                if len(corners) >= 3:
                    # Проверяем пересечение с каждой стороной препятствия
                    for i in range(len(corners)):
                        seg_start = Point(corners[i][0], corners[i][1])
                        seg_end = Point(corners[(i + 1) % len(corners)][0],
                                      corners[(i + 1) % len(corners)][1])
                        
                        intersection = ray_segment_intersection(origin, angle, seg_start, seg_end)
                        if intersection:
                            dist = distance(origin, intersection)
                            if dist < min_distance:
                                min_distance = dist
        
        return min_distance
    
    def add_obstacle(self, obstacle) -> None:
        """Добавляет препятствие в среду."""
        if isinstance(obstacle, RectangleObstacle):
            self.obstacles.add_placed_obstacle(obstacle)
    
    def remove_obstacle(self, obstacle) -> None:
        """Удаляет препятствие из среды."""
        if obstacle in self.obstacles.get_placed_obstacles():
            self.obstacles.get_placed_obstacles().remove(obstacle)
