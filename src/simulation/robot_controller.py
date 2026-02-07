"""
Контроллер управления роботом.
"""

import math
import pygame
from src.simulation.robot import Robot
from src.simulation.environment import Environment
from src.common.types import Point, RobotState


class RobotController:
    """Контроллер для управления роботом с клавиатуры."""
    
    def __init__(self, robot: Robot, environment: Environment):
        """
        Args:
            robot: экземпляр робота
            environment: среда для проверки коллизий
        """
        self.robot = robot
        self.environment = environment
        self.last_movement = (0.0, 0.0, 0.0)  # (dx, dy, dtheta)
    
    def handle_input(self, keys: pygame.key.ScancodeWrapper, dt: float) -> None:
        """
        Обрабатывает ввод с клавиатуры.
        
        Args:
            keys: состояние клавиш
            dt: время в секундах
        """
        dx, dy, dtheta = 0.0, 0.0, 0.0
        
        # Движение вперед/назад
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            if self.robot.move_forward(dt, self.environment):
                dx = self.robot.speed * dt * math.cos(self.robot.pose.theta)
                dy = self.robot.speed * dt * math.sin(self.robot.pose.theta)
        
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            if self.robot.move_backward(dt, self.environment):
                dx = -self.robot.speed * dt * math.cos(self.robot.pose.theta)
                dy = -self.robot.speed * dt * math.sin(self.robot.pose.theta)
        
        # Поворот
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.robot.rotate_left(dt)
            dtheta = -self.robot.rotation_speed * dt
        
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.robot.rotate_right(dt)
            dtheta = self.robot.rotation_speed * dt
        
        # Если нет движения, устанавливаем состояние IDLE
        if not any([keys[pygame.K_w], keys[pygame.K_UP], keys[pygame.K_s], 
                   keys[pygame.K_DOWN], keys[pygame.K_a], keys[pygame.K_LEFT],
                   keys[pygame.K_d], keys[pygame.K_RIGHT]]):
            self.robot.state = RobotState.IDLE
        
        self.last_movement = (dx, dy, dtheta)
    
    def is_collision(self) -> bool:
        """
        Проверяет, есть ли коллизия.
        
        Returns:
            True если есть коллизия
        """
        return not self.environment.is_valid_position(
            Point(self.robot.pose.x, self.robot.pose.y),
            self.robot.radius
        )
    
    def get_movement_delta(self) -> tuple[float, float, float]:
        """
        Возвращает дельту движения.
        
        Returns:
            (dx, dy, dtheta) - изменение позиции и угла
        """
        return self.last_movement

