"""
Режим локализации.
"""

import math
import pygame
from src.gui.modes.base_mode import BaseMode
from src.common.types import SimulationMode, Point
from src.simulation.robot import Robot
from src.simulation.environment import Environment
from src.simulation.lidar import Lidar


class LocalizationMode(BaseMode):
    """Режим локализации на известной карте."""
    
    def __init__(self, robot: Robot, environment: Environment, lidar: Lidar):
        super().__init__(SimulationMode.LOCALIZATION)
        self.robot = robot
        self.environment = environment
        self.lidar = lidar
        self.show_lidar = True
        self.last_scan = None
        self.estimated_pose = None
        self.confidence = 0.0
        self._scan_counter = 0
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Обрабатывает событие."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_l:
                print("Загрузка карты...")
    
    def update(self, dt: float, keys: pygame.key.ScancodeWrapper) -> None:
        """Обновляет состояние режима."""
        # Управление роботом (WASD)
        speed = self.robot.speed * dt
        rotation_speed = self.robot.rotation_speed * dt
        gx1 = self.environment.grid_left
        gy1 = self.environment.grid_top
        gx2 = self.environment.grid_right
        gy2 = self.environment.grid_bottom
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            new_x = self.robot.pose.x + speed * math.cos(self.robot.pose.theta)
            new_y = self.robot.pose.y + speed * math.sin(self.robot.pose.theta)
            if (gx1 + self.robot.radius <= new_x <= gx2 - self.robot.radius and
                gy1 + self.robot.radius <= new_y <= gy2 - self.robot.radius and
                self.environment.is_valid_position(Point(new_x, new_y), self.robot.radius)):
                self.robot.pose.x = new_x
                self.robot.pose.y = new_y
                self.robot.add_trajectory_point()
        
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            new_x = self.robot.pose.x - speed * math.cos(self.robot.pose.theta)
            new_y = self.robot.pose.y - speed * math.sin(self.robot.pose.theta)
            if (gx1 + self.robot.radius <= new_x <= gx2 - self.robot.radius and
                gy1 + self.robot.radius <= new_y <= gy2 - self.robot.radius and
                self.environment.is_valid_position(Point(new_x, new_y), self.robot.radius)):
                self.robot.pose.x = new_x
                self.robot.pose.y = new_y
                self.robot.add_trajectory_point()
        
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.robot.pose.theta -= rotation_speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.robot.pose.theta += rotation_speed
        
        while self.robot.pose.theta > 2 * math.pi:
            self.robot.pose.theta -= 2 * math.pi
        while self.robot.pose.theta < 0:
            self.robot.pose.theta += 2 * math.pi
        
        # Скан лидара для алгоритма локализации (не отображается на поле)
        self._scan_counter += 1
        if self._scan_counter % 3 == 0 and self.show_lidar:
            self.last_scan = self.lidar.scan(self.robot, self.environment)
    
    def render(self, screen: pygame.Surface) -> None:
        """Отрисовывает режим."""
        pass
    
    def on_mouse_click(self, pos: tuple, button: int) -> None:
        """Обрабатывает клик мыши."""
        if button == 3:  # ПКМ - телепортация робота
            self.robot.set_position(pos[0], pos[1])

