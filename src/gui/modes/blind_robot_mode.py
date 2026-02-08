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
        
        # Кэш для производительности
        self._fog_surface = None
        self._visible_surface = None
        self._last_visibility_size = 0
        self._scan_counter = 0
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Обрабатывает событие."""
        pass
    
    def update(self, dt: float, keys: pygame.key.ScancodeWrapper) -> None:
        """Обновляет состояние режима."""
        import math
        
        # Управление роботом
        speed = self.robot.speed * dt
        rotation_speed = self.robot.rotation_speed * dt
        
        # Параметры сетки (должны совпадать с редактором карты)
        GRID_START_X = 200
        GRID_START_Y = 100
        GRID_END_X = 1200
        GRID_END_Y = 1100
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            new_x = self.robot.pose.x + speed * math.cos(self.robot.pose.theta)
            new_y = self.robot.pose.y + speed * math.sin(self.robot.pose.theta)
            from src.common.types import Point
            # Проверяем границы сетки
            if (GRID_START_X + self.robot.radius <= new_x <= GRID_END_X - self.robot.radius and
                GRID_START_Y + self.robot.radius <= new_y <= GRID_END_Y - self.robot.radius and
                self.environment.is_valid_position(Point(new_x, new_y), self.robot.radius)):
                self.robot.pose.x = new_x
                self.robot.pose.y = new_y
                self.robot.add_trajectory_point()
        
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            new_x = self.robot.pose.x - speed * math.cos(self.robot.pose.theta)
            new_y = self.robot.pose.y - speed * math.sin(self.robot.pose.theta)
            from src.common.types import Point
            # Проверяем границы сетки
            if (GRID_START_X + self.robot.radius <= new_x <= GRID_END_X - self.robot.radius and
                GRID_START_Y + self.robot.radius <= new_y <= GRID_END_Y - self.robot.radius and
                self.environment.is_valid_position(Point(new_x, new_y), self.robot.radius)):
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
        
        # Сканирование лидаром (только раз в несколько кадров для производительности)
        self._scan_counter += 1
        
        # Сканируем каждые 3 кадра (для лучшей производительности)
        if self._scan_counter % 3 == 0:
            self.last_scan = self.lidar.scan(self.robot, self.environment)
            if self.last_scan:
                self.scan_history.append(self.last_scan)
                # Обновляем карту видимости только при новом скане
                self._update_visibility_map()
    
    def _update_visibility_map(self) -> None:
        """Обновляет карту видимости на основе сканов."""
        if not self.last_scan:
            return
        
        # Добавляем область вокруг робота (базовая видимость)
        robot_cell_x = int(self.robot.pose.x / 10)  # Увеличиваем разрешение для производительности
        robot_cell_y = int(self.robot.pose.y / 10)
        
        # Радиус видимости вокруг робота (базовая область)
        base_visibility_radius = 15  # ячеек
        
        for dx in range(-base_visibility_radius, base_visibility_radius + 1):
            for dy in range(-base_visibility_radius, base_visibility_radius + 1):
                if dx*dx + dy*dy <= base_visibility_radius * base_visibility_radius:
                    self.visibility_map.add((robot_cell_x + dx, robot_cell_y + dy))
        
        # Добавляем области вдоль лучей лидара (оптимизировано - каждый 5-й луч)
        robot_point = (self.robot.pose.x, self.robot.pose.y)
        for i in range(0, len(self.last_scan.points), 5):  # Каждый 5-й луч
            if i >= len(self.last_scan.distances):
                continue
            
            point = self.last_scan.points[i]
            
            # Добавляем ячейки вдоль луча от робота до точки
            start_x, start_y = robot_point
            end_x, end_y = point.x, point.y
            
            # Упрощенная интерполяция - меньше точек
            steps = max(1, int(self.last_scan.distances[i] / 20))  # Меньше шагов
            for step in range(0, steps + 1, 2):  # Каждый второй шаг
                t = step / max(steps, 1)
                x = start_x + t * (end_x - start_x)
                y = start_y + t * (end_y - start_y)
                
                cell_x = int(x / 10)
                cell_y = int(y / 10)
                
                # Добавляем только центральную точку (без области вокруг)
                self.visibility_map.add((cell_x, cell_y))
    
    def render(self, screen: pygame.Surface) -> None:
        """Отрисовывает режим."""
        # Отрисовка тумана войны
        self._render_fog_of_war(screen)
        
        # Отрисовка открытых препятствий
        self._render_revealed_obstacles(screen)
    
    def _render_fog_of_war(self, screen: pygame.Surface) -> None:
        """Отрисовывает туман войны (оптимизированная версия)."""
        # Кэшируем поверхность тумана
        if self._fog_surface is None:
            self._fog_surface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            self._fog_surface.fill((*self.fog_color, 250))
        
        # Создаем маску для видимых областей (только если изменилась карта видимости)
        if self._last_visibility_size != len(self.visibility_map):
            self._last_visibility_size = len(self.visibility_map)
            visible_surface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            visible_surface.fill((0, 0, 0, 0))
            
            # Рисуем видимые области (увеличенный размер для лучшей видимости)
            for cell_x, cell_y in self.visibility_map:
                world_x = cell_x * 10
                world_y = cell_y * 10
                # Рисуем белый круг в видимых областях
                pygame.draw.circle(visible_surface, (255, 255, 255, 255), 
                                 (int(world_x), int(world_y)), 12)
            
            # Обновляем кэш видимой поверхности
            self._visible_surface = visible_surface
        
        # Применяем видимые области к туману
        if self._visible_surface is not None:
            fog_copy = self._fog_surface.copy()
            fog_copy.blit(self._visible_surface, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
            screen.blit(fog_copy, (0, 0))
        else:
            # Если видимая поверхность еще не создана, просто показываем туман
            screen.blit(self._fog_surface, (0, 0))
    
    def _render_revealed_obstacles(self, screen: pygame.Surface) -> None:
        """Отрисовывает препятствия в видимых областях."""
        for obstacle in self.environment.obstacles.get_placed_obstacles():
            if isinstance(obstacle, RectangleObstacle):
                # Получаем углы препятствия (нужны для отрисовки в любом случае)
                corners = obstacle.get_corners()
                
                # Проверяем, видно ли препятствие (оптимизированная проверка)
                center_x = obstacle.x
                center_y = obstacle.y
                cell_x = int(center_x / 10)
                cell_y = int(center_y / 10)
                is_visible = (cell_x, cell_y) in self.visibility_map
                
                # Если центр не виден, проверяем углы
                if not is_visible:
                    for corner in corners:
                        cell_x = int(corner[0] / 10)
                        cell_y = int(corner[1] / 10)
                        if (cell_x, cell_y) in self.visibility_map:
                            is_visible = True
                            break
                
                if is_visible and len(corners) >= 3:
                    pygame.draw.polygon(screen, (255, 255, 0), corners)
                    pygame.draw.polygon(screen, (200, 200, 0), corners, 2)
    
    def on_mouse_click(self, pos: tuple, button: int) -> None:
        """Обрабатывает клик мыши."""
        pass
    
    def clear_history(self) -> None:
        """Очищает историю сканов."""
        self.scan_history = []
        self.visibility_map.clear()
        # Сбрасываем кэш поверхностей
        if hasattr(self, '_fog_surface'):
            self._fog_surface = None
        if hasattr(self, '_visible_surface'):
            self._visible_surface = None
        if hasattr(self, '_last_visibility_size'):
            self._last_visibility_size = 0

