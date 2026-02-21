"""
Режим картографирования.
"""

import pygame
import time
import math
from src.gui.modes.base_mode import BaseMode
from src.common.types import SimulationMode, Point
from src.simulation.robot import Robot
from src.simulation.environment import Environment
from src.simulation.lidar import Lidar


class MappingMode(BaseMode):
    """Режим картографирования с ручным управлением роботом."""
    
    def __init__(self, robot: Robot, environment: Environment, lidar: Lidar):
        super().__init__(SimulationMode.MAPPING)
        self.robot = robot
        self.environment = environment
        self.lidar = lidar
        self.show_lidar = True
        self.lidar_mode = "rays"  # "rays" или "points"
        self.last_scan = None
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Обрабатывает событие."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                # Сохранить карту
                print("Сохранение карты...")
                # TODO: реализовать сохранение карты
            elif event.key == pygame.K_l:
                # Переключить визуализацию лидара
                self.show_lidar = not self.show_lidar
    
    def update(self, dt: float, keys: pygame.key.ScancodeWrapper) -> None:
        """Обновляет состояние режима."""
        # Управление роботом
        speed = self.robot.speed * dt
        rotation_speed = self.robot.rotation_speed * dt
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            # Движение вперед
            new_x = self.robot.pose.x + speed * math.cos(self.robot.pose.theta)
            new_y = self.robot.pose.y + speed * math.sin(self.robot.pose.theta)
            if self.environment.is_valid_position(Point(new_x, new_y), self.robot.radius):
                # Обновляем одометрию
                self.robot._update_odometry(speed, 0.0)
                self.robot.pose.x = new_x
                self.robot.pose.y = new_y
                self.robot.add_trajectory_point()
        
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            # Движение назад
            new_x = self.robot.pose.x - speed * math.cos(self.robot.pose.theta)
            new_y = self.robot.pose.y - speed * math.sin(self.robot.pose.theta)
            if self.environment.is_valid_position(Point(new_x, new_y), self.robot.radius):
                # Обновляем одометрию
                self.robot._update_odometry(-speed, 0.0)
                self.robot.pose.x = new_x
                self.robot.pose.y = new_y
                self.robot.add_trajectory_point()
        
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            # Поворот влево
            self.robot.pose.theta -= rotation_speed
            self.robot._update_odometry(0.0, -rotation_speed)
        
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            # Поворот вправо
            self.robot.pose.theta += rotation_speed
            self.robot._update_odometry(0.0, rotation_speed)
        
        # Нормализация угла
        while self.robot.pose.theta > 2 * math.pi:
            self.robot.pose.theta -= 2 * math.pi
        while self.robot.pose.theta < 0:
            self.robot.pose.theta += 2 * math.pi
        
        # Сканирование лидаром
        if self.show_lidar:
            self.last_scan = self.lidar.scan(self.robot, self.environment)
    
    def render(self, screen: pygame.Surface) -> None:
        """Отрисовывает режим."""
        # Режим отрисовывается через Renderer в main_window
        pass
    
    def on_mouse_click(self, pos: tuple, button: int) -> None:
        """Обрабатывает клик мыши."""
        pass

