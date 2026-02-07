"""
Алгоритм Bresenham для получения ячеек вдоль линии.
"""

from typing import List, Tuple


def bresenham_line(x0: int, y0: int, x1: int, y1: int) -> List[Tuple[int, int]]:
    """
    Возвращает все ячейки между двумя точками используя алгоритм Bresenham.
    
    Args:
        x0, y0: начальная точка
        x1, y1: конечная точка
        
    Returns:
        Список кортежей (x, y) ячеек вдоль линии
    """
    points: List[Tuple[int, int]] = []
    
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    
    err = dx - dy
    x, y = x0, y0
    
    while True:
        points.append((x, y))
        
        if x == x1 and y == y1:
            break
        
        e2 = 2 * err
        
        if e2 > -dy:
            err -= dy
            x += sx
        
        if e2 < dx:
            err += dx
            y += sy
    
    return points

