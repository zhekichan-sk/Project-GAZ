import pygame
import math


class RectangleObstacle:
    """Класс для представления прямоугольного препятствия."""
    def __init__(self, x: float, y: float, width: float, height: float, angle: float = 0.0):
        """
        Args:
            x, y: координаты центра препятствия
            width: длина препятствия
            height: ширина препятствия
            angle: угол поворота в градусах
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.angle = angle  # угол в градусах
    
    def get_rect(self):
        """Возвращает pygame.Rect для простых случаев (без поворота)."""
        return pygame.Rect(
            self.x - self.width / 2,
            self.y - self.height / 2,
            self.width,
            self.height
        )
    
    def get_corners(self):
        """Возвращает координаты углов прямоугольника с учетом поворота."""
        # Углы относительно центра до поворота
        corners = [
            (-self.width / 2, -self.height / 2),
            (self.width / 2, -self.height / 2),
            (self.width / 2, self.height / 2),
            (-self.width / 2, self.height / 2)
        ]
        
        # Применяем поворот
        angle_rad = math.radians(self.angle)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        
        rotated_corners = []
        for dx, dy in corners:
            # Поворот вокруг центра
            rx = dx * cos_a - dy * sin_a
            ry = dx * sin_a + dy * cos_a
            # Смещение на позицию центра
            rotated_corners.append((self.x + rx, self.y + ry))
        
        return rotated_corners
    
    def contains_point(self, px: float, py: float) -> bool:
        """Проверяет, содержит ли препятствие точку (px, py)."""
        # Преобразуем точку в локальные координаты (относительно центра)
        dx = px - self.x
        dy = py - self.y
        
        # Обратный поворот
        angle_rad = math.radians(-self.angle)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        
        local_x = dx * cos_a - dy * sin_a
        local_y = dx * sin_a + dy * cos_a
        
        # Проверяем, находится ли точка внутри прямоугольника
        return abs(local_x) <= self.width / 2 and abs(local_y) <= self.height / 2
    
    def set_position(self, x: float, y: float):
        """Устанавливает новую позицию препятствия."""
        self.x = x
        self.y = y


class Obstacles:
    """Класс для управления препятствиями на карте."""
    def __init__(self, obstacles: list = None):
        """
        Args:
            obstacles: список препятствий (может быть list[tuple] для совместимости 
                      или list[RectangleObstacle] для новых препятствий)
        """
        self.obstacles = obstacles if obstacles is not None else []
        self.placed_obstacles = []  # Размещенные на карте препятствия

    def get_obstacles(self):
        """Возвращает список препятствий (для совместимости со старым кодом)."""
        return self.obstacles

    def set_obstacles(self, obstacles: list):
        """Устанавливает список препятствий."""
        self.obstacles = obstacles

    def add_obstacle(self, obstacle):
        """Добавляет препятствие в список."""
        self.obstacles.append(obstacle)

    def remove_obstacle(self, obstacle):
        """Удаляет препятствие из списка."""
        if obstacle in self.obstacles:
            self.obstacles.remove(obstacle)
    
    def add_placed_obstacle(self, obstacle: RectangleObstacle):
        """Добавляет размещенное препятствие на карту."""
        self.placed_obstacles.append(obstacle)
    
    def get_placed_obstacles(self):
        """Возвращает список размещенных препятствий."""
        return self.placed_obstacles
    
    def clear_placed_obstacles(self):
        """Очищает список размещенных препятствий."""
        self.placed_obstacles = []