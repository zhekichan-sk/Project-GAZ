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
    
    def render_environment(self, env: Environment, draw_boundaries: bool = True) -> None:
        """Отрисовывает среду.
        
        Args:
            env: среда
            draw_boundaries: рисовать ли жёлтые границы (False для режима слепого робота — рисуются поверх тумана)
        """
        # Отрисовка сетки (границы из среды)
        gs = env.GRID_SIZE
        for x in range(env.grid_left, env.grid_right + 1, gs):
            pygame.draw.line(
                self.screen, self.colors['light_gray'],
                (x, env.grid_top), (x, env.grid_bottom), 1
            )
        for y in range(env.grid_top, env.grid_bottom + 1, gs):
            pygame.draw.line(
                self.screen, self.colors['light_gray'],
                (env.grid_left, y), (env.grid_right, y), 1
            )
        
        # Отрисовка препятствий
        if hasattr(env.obstacles, 'get_placed_obstacles'):
            for obstacle in env.obstacles.get_placed_obstacles():
                self._render_obstacle(obstacle)
        if draw_boundaries:
            for obstacle in getattr(env, 'boundary_obstacles', []):
                self._render_obstacle(obstacle)
    
    def render_boundary_obstacles(self, env: Environment) -> None:
        """Отрисовывает жёлтые границы сетки (для режима слепого робота поверх тумана)."""
        for obstacle in getattr(env, 'boundary_obstacles', []):
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
        """Отрисовывает точки лидара (зеленые индикаторы, оптимизировано)."""
        max_range = getattr(scan, 'max_range', 300.0)
        # Отрисовываем только каждый 10-й луч для производительности
        for i in range(0, len(scan.points), 10):
            if i < len(scan.distances) and scan.distances[i] < max_range:
                point = scan.points[i]
                # Только зеленые точки для индикации
                pygame.draw.circle(self.screen, self.colors['green'],
                                 (int(point.x), int(point.y)), 3)
    
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
    
    def render_minimap(self, grid: Optional[OccupancyGrid], robot_pose: Optional[Point] = None, 
                       estimated_pose: Optional[Point] = None, 
                       size: int = 200, position: tuple = None) -> None:
        """
        Отрисовывает мини-карту в правом верхнем углу.
        
        Args:
            grid: карта занятости для отображения
            robot_pose: реальная позиция робота (Point)
            estimated_pose: оцененная позиция робота (Point)
            size: размер мини-карты в пикселях
            position: позиция мини-карты (x, y), если None - правый верхний угол
        """
        if grid is None:
            return
        
        # Определяем позицию мини-карты (правый верхний угол)
        screen_width = self.screen.get_width()
        if position is None:
            minimap_x = screen_width - size - 10
            minimap_y = 10
        else:
            minimap_x, minimap_y = position
        
        # Создаем поверхность для мини-карты
        minimap_surface = pygame.Surface((size, size))
        minimap_surface.fill((50, 50, 50))  # Темно-серый фон
        
        # Масштабируем карту для мини-карты
        scale_x = size / grid.width
        scale_y = size / grid.height
        scale = min(scale_x, scale_y)
        
        # Отрисовываем карту
        for i in range(grid.height):
            for j in range(grid.width):
                cell_value = grid.get_cell(i, j)
                
                # Преобразуем в координаты мини-карты
                x = int(j * scale)
                y = int(i * scale)
                cell_size = max(1, int(scale))
                
                # Цвет в зависимости от вероятности занятости
                if cell_value < 0.4:  # Свободно
                    color = (255, 255, 255)  # Белый
                elif cell_value > 0.6:  # Занято
                    color = (0, 0, 0)  # Черный
                else:  # Неизвестно
                    color = (128, 128, 128)  # Серый
                
                pygame.draw.rect(minimap_surface, color, 
                                (x, y, cell_size, cell_size))
        
        # Отрисовываем реальную позицию робота (синий)
        if robot_pose:
            robot_i, robot_j = grid.world_to_grid(robot_pose)
            robot_x = int(robot_j * scale)
            robot_y = int(robot_i * scale)
            pygame.draw.circle(minimap_surface, (0, 150, 255), 
                             (robot_x, robot_y), max(2, int(scale * 2)))
        
        # Отрисовываем оцененную позицию робота (красный)
        if estimated_pose:
            est_i, est_j = grid.world_to_grid(estimated_pose)
            est_x = int(est_j * scale)
            est_y = int(est_i * scale)
            pygame.draw.circle(minimap_surface, (255, 0, 0), 
                             (est_x, est_y), max(2, int(scale * 2)))
        
        # Рамка мини-карты
        pygame.draw.rect(minimap_surface, (255, 255, 255), 
                        (0, 0, size, size), 2)
        
        # Отображаем мини-карту на экране
        self.screen.blit(minimap_surface, (minimap_x, minimap_y))

