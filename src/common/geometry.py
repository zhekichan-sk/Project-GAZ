"""
Геометрические утилиты для работы с точками, линиями и полигонами.
"""

import math
from typing import Optional

from .types import Point


def distance(p1: Point, p2: Point) -> float:
    """
    Вычисляет расстояние между двумя точками.
    
    Args:
        p1: Первая точка
        p2: Вторая точка
        
    Returns:
        Расстояние между точками
    """
    return math.sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2)


def angle_between(p1: Point, p2: Point) -> float:
    """
    Вычисляет угол в радианах от точки p1 к точке p2.
    
    Args:
        p1: Начальная точка
        p2: Конечная точка
        
    Returns:
        Угол в радианах в диапазоне [-π, π]
    """
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    return math.atan2(dy, dx)


def normalize_angle(angle: float) -> float:
    """
    Нормализует угол в диапазон [-π, π].
    
    Args:
        angle: Угол в радианах
        
    Returns:
        Нормализованный угол в диапазоне [-π, π]
    """
    while angle > math.pi:
        angle -= 2 * math.pi
    while angle < -math.pi:
        angle += 2 * math.pi
    return angle


def rotate_point(point: Point, origin: Point, angle: float) -> Point:
    """
    Поворачивает точку вокруг начала координат на заданный угол.
    
    Args:
        point: Точка для поворота
        origin: Центр поворота
        angle: Угол поворота в радианах
        
    Returns:
        Повернутая точка
    """
    # Переносим точку относительно начала координат
    dx = point.x - origin.x
    dy = point.y - origin.y
    
    # Поворачиваем
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    rotated_x = dx * cos_a - dy * sin_a
    rotated_y = dx * sin_a + dy * cos_a
    
    # Возвращаем обратно
    return Point(rotated_x + origin.x, rotated_y + origin.y)


def line_intersection(
    line1_start: Point,
    line1_end: Point,
    line2_start: Point,
    line2_end: Point,
) -> Optional[Point]:
    """
    Находит точку пересечения двух отрезков, если она существует.
    
    Args:
        line1_start: Начало первого отрезка
        line1_end: Конец первого отрезка
        line2_start: Начало второго отрезка
        line2_end: Конец второго отрезка
        
    Returns:
        Точка пересечения или None, если отрезки не пересекаются
    """
    x1, y1 = line1_start.x, line1_start.y
    x2, y2 = line1_end.x, line1_end.y
    x3, y3 = line2_start.x, line2_start.y
    x4, y4 = line2_end.x, line2_end.y
    
    # Вычисляем знаменатель
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    
    if abs(denom) < 1e-10:  # Отрезки параллельны
        return None
    
    # Параметры для первого отрезка
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    # Параметры для второго отрезка
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
    
    # Проверяем, что точка пересечения находится на обоих отрезках
    if 0 <= t <= 1 and 0 <= u <= 1:
        # Вычисляем координаты точки пересечения
        x = x1 + t * (x2 - x1)
        y = y1 + t * (y2 - y1)
        return Point(x, y)
    
    return None


def point_in_polygon(point: Point, polygon: list[Point]) -> bool:
    """
    Проверяет, находится ли точка внутри полигона (алгоритм ray casting).
    
    Args:
        point: Точка для проверки
        polygon: Список вершин полигона
        
    Returns:
        True, если точка внутри полигона, иначе False
    """
    if len(polygon) < 3:
        return False
    
    x, y = point.x, point.y
    n = len(polygon)
    inside = False
    
    p1x, p1y = polygon[0].x, polygon[0].y
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n].x, polygon[i % n].y
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    
    return inside


def ray_segment_intersection(
    ray_origin: Point,
    ray_angle: float,
    segment_start: Point,
    segment_end: Point,
) -> Optional[Point]:
    """
    Находит точку пересечения луча с отрезком.
    
    Args:
        ray_origin: Начало луча
        ray_angle: Угол луча в радианах
        segment_start: Начало отрезка
        segment_end: Конец отрезка
        
    Returns:
        Точка пересечения или None, если пересечения нет
    """
    # Направляющий вектор луча
    ray_dir = Point(math.cos(ray_angle), math.sin(ray_angle))
    
    # Вектор отрезка
    seg_dir = Point(segment_end.x - segment_start.x, segment_end.y - segment_start.y)
    
    # Вектор от начала луча до начала отрезка
    diff = Point(ray_origin.x - segment_start.x, ray_origin.y - segment_start.y)
    
    # Вычисляем знаменатель
    denom = seg_dir.y * ray_dir.x - seg_dir.x * ray_dir.y
    
    if abs(denom) < 1e-10:  # Луч и отрезок параллельны
        return None
    
    # Параметры
    t1 = (seg_dir.x * diff.y - seg_dir.y * diff.x) / denom
    t2 = (ray_dir.x * diff.y - ray_dir.y * diff.x) / denom
    
    # Проверяем, что пересечение находится на луче (t1 >= 0) и на отрезке (0 <= t2 <= 1)
    if t1 >= 0 and 0 <= t2 <= 1:
        x = ray_origin.x + t1 * ray_dir.x
        y = ray_origin.y + t1 * ray_dir.y
        return Point(x, y)
    
    return None

