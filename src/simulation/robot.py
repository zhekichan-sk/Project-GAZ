"""
Модель робота для симуляции.
"""

import math
import random
from typing import List
import pygame
from src.common.types import Pose, Point, RobotState
from src.common.geometry import normalize_angle
from src.simulation.environment import Environment


class Robot:
    """Модель робота с позицией и управлением."""
    
    def __init__(self, x: float = 400.0, y: float = 300.0, theta: float = 0.0,
                 radius: float = 15.0, speed: float = 100.0, rotation_speed: float = 2.0,
                 color: tuple = (0, 150, 255)):
        """
        Args:
            x, y: начальная позиция
            theta: начальная ориентация в радианах
            radius: радиус робота
            speed: линейная скорость (единиц/сек)
            rotation_speed: угловая скорость (рад/сек)
            color: цвет для отрисовки
        """
        self.pose = Pose(x, y, theta)
        self.radius = radius
        self.speed = speed
        self.rotation_speed = rotation_speed
        self.color = color
        self.trajectory: List[Point] = []
        self.state = RobotState.IDLE
        
        # Одометрия с накопленной ошибкой
        self.odometry_pose = Pose(x, y, theta)
        self.odometry_noise_linear = 0.0
        self.odometry_noise_angular = 0.0
    
    def move_forward(self, dt: float, environment: Environment) -> bool:
        """
        Движение вперед с проверкой коллизий.
        
        Args:
            dt: время в секундах
            environment: среда для проверки коллизий
            
        Returns:
            True если движение успешно, False если была коллизия
        """
        distance = self.speed * dt
        new_x = self.pose.x + distance * math.cos(self.pose.theta)
        new_y = self.pose.y + distance * math.sin(self.pose.theta)
        
        if environment.is_valid_position(Point(new_x, new_y), self.radius):
            self.pose.x = new_x
            self.pose.y = new_y
            self.pose.theta = normalize_angle(self.pose.theta)
            self._update_odometry(distance, 0.0)
            self.add_trajectory_point()
            self.state = RobotState.MOVING
            return True
        return False
    
    def move_backward(self, dt: float, environment: Environment) -> bool:
        """
        Движение назад с проверкой коллизий.
        
        Args:
            dt: время в секундах
            environment: среда для проверки коллизий
            
        Returns:
            True если движение успешно, False если была коллизия
        """
        distance = self.speed * dt
        new_x = self.pose.x - distance * math.cos(self.pose.theta)
        new_y = self.pose.y - distance * math.sin(self.pose.theta)
        
        if environment.is_valid_position(Point(new_x, new_y), self.radius):
            self.pose.x = new_x
            self.pose.y = new_y
            self.pose.theta = normalize_angle(self.pose.theta)
            self._update_odometry(-distance, 0.0)
            self.add_trajectory_point()
            self.state = RobotState.MOVING
            return True
        return False
    
    def rotate_left(self, dt: float) -> None:
        """Поворот влево."""
        self.pose.theta -= self.rotation_speed * dt
        self.pose.theta = normalize_angle(self.pose.theta)
        self._update_odometry(0.0, -self.rotation_speed * dt)
        self.state = RobotState.MOVING
    
    def rotate_right(self, dt: float) -> None:
        """Поворот вправо."""
        self.pose.theta += self.rotation_speed * dt
        self.pose.theta = normalize_angle(self.pose.theta)
        self._update_odometry(0.0, self.rotation_speed * dt)
        self.state = RobotState.MOVING
    
    def set_position(self, x: float, y: float, theta: float = None) -> None:
        """Устанавливает позицию робота (телепортация)."""
        self.pose.x = x
        self.pose.y = y
        if theta is not None:
            self.pose.theta = normalize_angle(theta)
        self.odometry_pose = Pose(x, y, self.pose.theta)
    
    def get_odometry(self) -> Pose:
        """
        Возвращает текущую одометрию (с накопленной ошибкой).
        
        Returns:
            Pose с позицией по одометрии
        """
        return Pose(self.odometry_pose.x, self.odometry_pose.y, self.odometry_pose.theta)
    
    def add_odometry_noise(self, noise_linear: float, noise_angular: float) -> None:
        """
        Устанавливает параметры шума одометрии.
        
        Args:
            noise_linear: стандартное отклонение линейного шума
            noise_angular: стандартное отклонение углового шума
        """
        self.odometry_noise_linear = noise_linear
        self.odometry_noise_angular = noise_angular
    
    def _update_odometry(self, linear_delta: float, angular_delta: float) -> None:
        """Обновляет одометрию с учетом шума."""
        # Добавляем шум к линейному перемещению
        if self.odometry_noise_linear > 0:
            linear_delta += random.gauss(0, self.odometry_noise_linear * abs(linear_delta))
        
        # Добавляем шум к угловому перемещению
        if self.odometry_noise_angular > 0:
            angular_delta += random.gauss(0, self.odometry_noise_angular * abs(angular_delta))
        
        # Обновляем одометрию
        self.odometry_pose.x += linear_delta * math.cos(self.odometry_pose.theta)
        self.odometry_pose.y += linear_delta * math.sin(self.odometry_pose.theta)
        self.odometry_pose.theta = normalize_angle(self.odometry_pose.theta + angular_delta)
    
    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает робота (круг + направление)."""
        x, y = int(self.pose.x), int(self.pose.y)
        radius = int(self.radius)
        
        # Тело робота
        pygame.draw.circle(surface, self.color, (x, y), radius)
        pygame.draw.circle(surface, (0, 0, 0), (x, y), radius, 2)
        
        # Направление
        end_x = x + radius * math.cos(self.pose.theta)
        end_y = y + radius * math.sin(self.pose.theta)
        pygame.draw.line(surface, (0, 0, 0), (x, y), (int(end_x), int(end_y)), 3)
    
    def draw_trajectory(self, surface: pygame.Surface) -> None:
        """Отрисовывает траекторию робота."""
        if len(self.trajectory) < 2:
            return
        
        points = [(int(p.x), int(p.y)) for p in self.trajectory]
        pygame.draw.lines(surface, (100, 100, 255), False, points, 2)
    
    def clear_trajectory(self) -> None:
        """Очищает траекторию."""
        self.trajectory = []
    
    def add_trajectory_point(self) -> None:
        """Добавляет текущую точку в траекторию."""
        self.trajectory.append(Point(self.pose.x, self.pose.y))
    
    @classmethod
    def from_config(cls, config: dict):
        """
        Создает робота из конфигурации.
        
        Args:
            config: словарь с параметрами робота
            
        Returns:
            Экземпляр Robot
        """
        robot_config = config.get('robot', {})
        lidar_config = config.get('lidar', {})
        
        start_pos = robot_config.get('start_position', [400, 300])
        start_angle = robot_config.get('start_angle', 0)
        
        robot = cls(
            x=start_pos[0],
            y=start_pos[1],
            theta=math.radians(start_angle),
            radius=robot_config.get('radius', 15.0),
            speed=robot_config.get('speed', 100.0),
            rotation_speed=robot_config.get('rotation_speed', 2.0),
            color=tuple(robot_config.get('color', [0, 150, 255]))
        )
        
        return robot
