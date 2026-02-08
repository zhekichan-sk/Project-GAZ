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
    
    def is_valid_position(self, point: Point, radius: float) -> bool:
        """
        Проверяет, является ли позиция валидной (нет коллизий).
        
        Args:
            point: точка для проверки
            radius: радиус объекта
            
        Returns:
            True если позиция валидна, False если есть коллизия
        """
        # Параметры сетки (должны совпадать с редактором карты)
        GRID_START_X = 200
        GRID_START_Y = 100
        GRID_END_X = 1200
        GRID_END_Y = 1100
        
        # Проверка границ сетки (робот должен ходить только по сетке)
        # Центр робота должен быть не ближе radius от границ сетки
        if point.x < GRID_START_X + radius or point.x > GRID_END_X - radius:
            return False
        if point.y < GRID_START_Y + radius or point.y > GRID_END_Y - radius:
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
        
        Args:
            origin: начало луча
            angle: угол луча в радианах
            max_dist: максимальное расстояние
            
        Returns:
            Расстояние до препятствия или max_dist если препятствия нет
        """
        # Конечная точка луча
        end_x = origin.x + max_dist * math.cos(angle)
        end_y = origin.y + max_dist * math.sin(angle)
        end_point = Point(end_x, end_y)
        
        min_distance = max_dist
        
        # Проверка границ среды
        # Левая граница
        if math.cos(angle) < 0:
            t = -origin.x / math.cos(angle)
            if t > 0:
                y = origin.y + t * math.sin(angle)
                if 0 <= y <= self.height:
                    min_distance = min(min_distance, t)
        
        # Правая граница
        if math.cos(angle) > 0:
            t = (self.width - origin.x) / math.cos(angle)
            if t > 0:
                y = origin.y + t * math.sin(angle)
                if 0 <= y <= self.height:
                    min_distance = min(min_distance, t)
        
        # Верхняя граница
        if math.sin(angle) < 0:
            t = -origin.y / math.sin(angle)
            if t > 0:
                x = origin.x + t * math.cos(angle)
                if 0 <= x <= self.width:
                    min_distance = min(min_distance, t)
        
        # Нижняя граница
        if math.sin(angle) > 0:
            t = (self.height - origin.y) / math.sin(angle)
            if t > 0:
                x = origin.x + t * math.cos(angle)
                if 0 <= x <= self.width:
                    min_distance = min(min_distance, t)
        
        # Проверка препятствий
        for obstacle in self.obstacles.get_placed_obstacles():
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
