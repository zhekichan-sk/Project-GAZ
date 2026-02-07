"""
Рендерер для отрисовки всех элементов симуляции.
"""

import pygame
import numpy as np
from typing import List, Optional
from src.common.types import Point
from src.simulation.environment import Environment
from src.simulation.robot import Robot
from src.simulation.lidar import LidarScan
from src.simulation.obstacles import Obstacles
from src.mapping.occupancy_grid import OccupancyGrid


class Renderer:
    """Рендерер для отрисовки элементов симуляции."""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.colors = {
            'black': (0, 0, 0),
            'white': (255, 255, 255),
            'light_gray': (200, 200, 200),
            'red': (255, 0, 0),
            'green': (0, 255, 0),
            'yellow': (255, 255, 0),
            'blue': (0, 0, 255),
            'robot': (0, 150, 255),
            'trajectory': (100, 100, 255),
            'goal': (255, 0, 0),
            'path': (0, 255, 0),
        }
    
    def render_environment(self, env: Environment) -> None:
        """Отрисовывает среду."""
        # Отрисовка сетки
        grid_size = 100
        grid_start_x = 200
        grid_start_y = 100
        grid_end_x = 1200
        grid_end_y = 1100
        
        for x in range(grid_start_x, grid_end_x + 1, grid_size):
            pygame.draw.line(
                self.screen, self.colors['light_gray'],
                (x, grid_start_y), (x, grid_end_y), 1
            )
        for y in range(grid_start_y, grid_end_y + 1, grid_size):
            pygame.draw.line(
                self.screen, self.colors['light_gray'],
                (grid_start_x, y), (grid_end_x, y), 1
            )
        
        # Отрисовка препятствий
        if hasattr(env.obstacles, 'get_placed_obstacles'):
            for obstacle in env.obstacles.get_placed_obstacles():
                self._render_obstacle(obstacle)
    
    def _render_obstacle(self, obstacle) -> None:
        """Отрисовывает одно препятствие."""
        if hasattr(obstacle, 'get_corners'):
            corners = obstacle.get_corners()
            if len(corners) >= 3:
                pygame.draw.polygon(self.screen, self.colors['yellow'], corners)
                pygame.draw.polygon(self.screen, (200, 200, 0), corners, 2)
    
    def render_robot(self, robot: Robot) -> None:
        """Отрисовывает робота."""
        x, y = int(robot.pose.x), int(robot.pose.y)
        radius = int(robot.radius)
        
        # Тело робота
        pygame.draw.circle(self.screen, self.colors['robot'], (x, y), radius)
        pygame.draw.circle(self.screen, self.colors['black'], (x, y), radius, 2)
        
        # Направление
        import math
        end_x = x + radius * math.cos(robot.pose.theta)
        end_y = y + radius * math.sin(robot.pose.theta)
        pygame.draw.line(
            self.screen, self.colors['black'],
            (x, y), (int(end_x), int(end_y)), 3
        )
    
    def render_lidar_scan(self, scan: LidarScan, mode: str = "points") -> None:
        """Отрисовывает скан лидара."""
        # Всегда используем только точки для лучшей производительности
        self._render_lidar_points(scan)
    
    def _render_lidar_points(self, scan: LidarScan) -> None:
        """Отрисовывает точки лидара (зеленые индикаторы)."""
        max_range = getattr(scan, 'max_range', 300.0)
        for i, point in enumerate(scan.points):
            if i < len(scan.distances) and scan.distances[i] < max_range:
                # Только зеленые точки для индикации
                pygame.draw.circle(self.screen, self.colors['green'],
                                 (int(point.x), int(point.y)), 2)
    
    def render_occupancy_grid(self, grid: Optional[OccupancyGrid], alpha: int = 128) -> None:
        """
        Отрисовывает карту занятости.
        
        Args:
            grid: OccupancyGrid для отрисовки
            alpha: прозрачность [0-255]
        """
        if grid is None:
            return
        
        # Конвертируем карту в изображение
        image = grid.to_image()
        
        # Создаем поверхность для отрисовки
        # Преобразуем grayscale в RGB для pygame
        rgb_image = np.stack([image, image, image], axis=-1)
        surface = pygame.surfarray.make_surface(rgb_image.swapaxes(0, 1))
        surface.set_alpha(alpha)
        
        # Вычисляем позицию для отрисовки
        origin_x = int(grid.origin.x)
        origin_y = int(grid.origin.y)
        
        # Масштабируем поверхность до нужного размера
        scaled_width = int(grid.width * grid.resolution)
        scaled_height = int(grid.height * grid.resolution)
        scaled_surface = pygame.transform.scale(surface, (scaled_width, scaled_height))
        
        # Отрисовываем на экране
        self.screen.blit(scaled_surface, (origin_x, origin_y))
    
    def render_path(self, path: List[Point], color: tuple = None) -> None:
        """Отрисовывает путь."""
        if not path or len(path) < 2:
            return
        
        path_color = color or self.colors['path']
        points = [(int(p.x), int(p.y)) for p in path]
        pygame.draw.lines(self.screen, path_color, False, points, 3)
        
        # Отмечаем точки пути
        for point in path:
            pygame.draw.circle(self.screen, path_color,
                             (int(point.x), int(point.y)), 5)
    
    def render_goal(self, goal: Point) -> None:
        """Отрисовывает цель."""
        pygame.draw.circle(self.screen, self.colors['goal'],
                         (int(goal.x), int(goal.y)), 15)
        pygame.draw.circle(self.screen, self.colors['black'],
                         (int(goal.x), int(goal.y)), 15, 2)
    
    def render_trajectory(self, trajectory: List[Point]) -> None:
        """Отрисовывает траекторию робота."""
        if len(trajectory) < 2:
            return
        
        points = [(int(p.x), int(p.y)) for p in trajectory]
        pygame.draw.lines(self.screen, self.colors['trajectory'],
                         False, points, 2)

