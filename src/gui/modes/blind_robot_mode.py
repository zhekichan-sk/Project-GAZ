"""
Режим слепого робота (Scanner Sombre style).
"""

import pygame
import math
import numpy as np
from typing import Set, Tuple
from src.gui.modes.base_mode import BaseMode
from src.common.types import SimulationMode, Point, Pose
from src.simulation.robot import Robot
from src.simulation.environment import Environment
from src.simulation.lidar import Lidar, LidarScan
from src.simulation.obstacles import RectangleObstacle
from src.mapping.occupancy_grid import OccupancyGrid
from src.mapping.mapper import Mapper


class BlindRobotMode(BaseMode):
    """Режим слепого робота - карта скрыта, лидар постепенно открывает область."""
    
    def __init__(self, robot: Robot, environment: Environment, lidar: Lidar):
        super().__init__(SimulationMode.MAPPING)
        self.robot = robot
        self.environment = environment
        self.lidar = lidar
        
        # Карта для визуализации открытых областей
        self.visibility_map: Set[Tuple[int, int]] = set()
        self.scan_history: list[LidarScan] = []
        
        # Параметры визуализации
        self.fog_color = (20, 20, 20)  # Темный туман
        self.revealed_color = (255, 255, 255)  # Белый для открытых областей
        
        # Последний скан
        self.last_scan: LidarScan = None
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Обрабатывает событие."""
        pass
    
    def update(self, dt: float, keys: pygame.key.ScancodeWrapper) -> None:
        """Обновляет состояние режима."""
        import math
        
        # Управление роботом
        speed = self.robot.speed * dt
        rotation_speed = self.robot.rotation_speed * dt
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            new_x = self.robot.pose.x + speed * math.cos(self.robot.pose.theta)
            new_y = self.robot.pose.y + speed * math.sin(self.robot.pose.theta)
            from src.common.types import Point
            if self.environment.is_valid_position(Point(new_x, new_y), self.robot.radius):
                self.robot.pose.x = new_x
                self.robot.pose.y = new_y
                self.robot.add_trajectory_point()
        
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            new_x = self.robot.pose.x - speed * math.cos(self.robot.pose.theta)
            new_y = self.robot.pose.y - speed * math.sin(self.robot.pose.theta)
            from src.common.types import Point
            if self.environment.is_valid_position(Point(new_x, new_y), self.robot.radius):
                self.robot.pose.x = new_x
                self.robot.pose.y = new_y
                self.robot.add_trajectory_point()
        
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.robot.pose.theta -= rotation_speed
        
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.robot.pose.theta += rotation_speed
        
        # Нормализация угла
        while self.robot.pose.theta > 2 * math.pi:
            self.robot.pose.theta -= 2 * math.pi
        while self.robot.pose.theta < 0:
            self.robot.pose.theta += 2 * math.pi
        
        # Сканирование лидаром
        self.last_scan = self.lidar.scan(self.robot, self.environment)
        self.scan_history.append(self.last_scan)
        
        # Обновляем карту видимости
        self._update_visibility_map()
    
    def _update_visibility_map(self) -> None:
        """Обновляет карту видимости на основе сканов."""
        if not self.last_scan:
            return
        
        # Добавляем область вокруг робота (базовая видимость)
        robot_cell_x = int(self.robot.pose.x / 5)  # Разрешение 5 пикселей на ячейку
        robot_cell_y = int(self.robot.pose.y / 5)
        
        # Радиус видимости вокруг робота (базовая область)
        base_visibility_radius = 20  # ячеек
        
        for dx in range(-base_visibility_radius, base_visibility_radius + 1):
            for dy in range(-base_visibility_radius, base_visibility_radius + 1):
                if dx*dx + dy*dy <= base_visibility_radius * base_visibility_radius:
                    self.visibility_map.add((robot_cell_x + dx, robot_cell_y + dy))
        
        # Добавляем области вдоль лучей лидара
        robot_point = (self.robot.pose.x, self.robot.pose.y)
        for i, point in enumerate(self.last_scan.points):
            if i >= len(self.last_scan.distances):
                continue
            
            # Добавляем ячейки вдоль луча от робота до точки
            start_x, start_y = robot_point
            end_x, end_y = point.x, point.y
            
            # Линейная интерполяция для получения всех точек вдоль луча
            steps = int(self.last_scan.distances[i] / 5) + 1
            for step in range(steps + 1):
                t = step / max(steps, 1)
                x = start_x + t * (end_x - start_x)
                y = start_y + t * (end_y - start_y)
                
                cell_x = int(x / 5)
                cell_y = int(y / 5)
                
                # Добавляем небольшую область вокруг каждой точки
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        self.visibility_map.add((cell_x + dx, cell_y + dy))
    
    def render(self, screen: pygame.Surface) -> None:
        """Отрисовывает режим."""
        # Отрисовка тумана войны
        self._render_fog_of_war(screen)
        
        # Отрисовка открытых препятствий
        self._render_revealed_obstacles(screen)
    
    def _render_fog_of_war(self, screen: pygame.Surface) -> None:
        """Отрисовывает туман войны."""
        # Создаем поверхность для тумана
        fog_surface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        fog_surface.fill((*self.fog_color, 250))  # RGBA - темный туман
        
        # Создаем маску для видимых областей
        visible_surface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        visible_surface.fill((0, 0, 0, 0))
        
        # Рисуем видимые области
        for cell_x, cell_y in self.visibility_map:
            world_x = cell_x * 5
            world_y = cell_y * 5
            # Рисуем белый круг в видимых областях
            pygame.draw.circle(visible_surface, (255, 255, 255, 255), 
                             (int(world_x), int(world_y)), 8)
        
        # Применяем размытие для плавных краев
        # Вычитаем видимые области из тумана
        fog_surface.blit(visible_surface, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
        
        screen.blit(fog_surface, (0, 0))
    
    def _render_revealed_obstacles(self, screen: pygame.Surface) -> None:
        """Отрисовывает препятствия в видимых областях."""
        for obstacle in self.environment.obstacles.get_placed_obstacles():
            if isinstance(obstacle, RectangleObstacle):
                # Проверяем, видно ли препятствие
                corners = obstacle.get_corners()
                is_visible = False
                for corner in corners:
                    cell_x = int(corner[0] / 5)
                    cell_y = int(corner[1] / 5)
                    if (cell_x, cell_y) in self.visibility_map:
                        is_visible = True
                        break
                
                if is_visible:
                    if len(corners) >= 3:
                        pygame.draw.polygon(screen, (255, 255, 0), corners)
                        pygame.draw.polygon(screen, (200, 200, 0), corners, 2)
    
    def on_mouse_click(self, pos: tuple, button: int) -> None:
        """Обрабатывает клик мыши."""
        pass
    
    def clear_history(self) -> None:
        """Очищает историю сканов."""
        self.scan_history = []
        self.visibility_map.clear()

