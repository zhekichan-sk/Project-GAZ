"""
Виртуальный лидар для симуляции.
"""

import math
import time
from dataclasses import dataclass
from typing import List
import numpy as np
import pygame
from src.common.types import Point, Pose
from src.simulation.robot import Robot
from src.simulation.environment import Environment


@dataclass
class LidarScan:
    """Результат сканирования лидара."""
    angles: np.ndarray
    distances: np.ndarray
    points: List[Point]
    timestamp: float
    robot_pose: Pose
    max_range: float = 300.0  # Максимальная дальность лидара


class Lidar:
    """Виртуальный лидар (лазерный дальномер)."""
    
    def __init__(self, num_rays: int = 360, max_range: float = 300.0,
                 fov: float = 360.0, noise_std: float = 1.0, angle_resolution: float = 1.0):
        """
        Args:
            num_rays: количество лучей
            max_range: максимальная дальность
            fov: угол обзора в градусах (360 = полный круг)
            noise_std: стандартное отклонение шума
            angle_resolution: разрешение по углу в градусах
        """
        self.num_rays = num_rays
        self.max_range = max_range
        self.fov = math.radians(fov)
        self.noise_std = noise_std
        self.angle_resolution = math.radians(angle_resolution)
    
    def scan(self, robot: Robot, environment: Environment) -> LidarScan:
        """
        Выполняет сканирование.
        
        Args:
            robot: робот с позицией
            environment: среда для трассировки лучей
            
        Returns:
            LidarScan с результатами сканирования
        """
        angles = self.get_ray_angles()
        distances = np.zeros(self.num_rays)
        points: List[Point] = []
        
        robot_origin = Point(robot.pose.x, robot.pose.y)
        
        for i, angle in enumerate(angles):
            # Глобальный угол луча
            global_angle = robot.pose.theta + angle
            
            # Трассировка луча
            distance = environment.raycast(robot_origin, global_angle, self.max_range)
            
            # Добавление гауссовского шума
            if self.noise_std > 0:
                distance += np.random.normal(0, self.noise_std)
                distance = max(0, min(distance, self.max_range))
            
            distances[i] = distance
            
            # Конвертация в глобальные координаты
            point_x = robot.pose.x + distance * math.cos(global_angle)
            point_y = robot.pose.y + distance * math.sin(global_angle)
            points.append(Point(point_x, point_y))
        
        return LidarScan(
            angles=angles,
            distances=distances,
            points=points,
            timestamp=time.time(),
            robot_pose=robot.pose,
            max_range=self.max_range
        )
    
    def get_ray_angles(self) -> np.ndarray:
        """
        Возвращает массив углов лучей.
        
        Returns:
            Массив углов в радианах
        """
        if self.fov >= 2 * math.pi:
            # Полный круг
            return np.linspace(0, 2 * math.pi, self.num_rays, endpoint=False)
        else:
            # Частичный обзор
            start_angle = -self.fov / 2
            return np.linspace(start_angle, start_angle + self.fov, self.num_rays)
    
    def draw_rays(self, surface: pygame.Surface, robot: Robot, scan: LidarScan, 
                  color: tuple = (0, 255, 0)) -> None:
        """
        Визуализация лучей лидара.
        
        Args:
            surface: поверхность для отрисовки
            robot: робот
            scan: результаты сканирования
            color: цвет лучей
        """
        robot_x = int(robot.pose.x)
        robot_y = int(robot.pose.y)
        
        for i, point in enumerate(scan.points):
            if i < len(scan.distances) and scan.distances[i] < self.max_range:
                # Интенсивность зависит от расстояния
                distance = scan.distances[i]
                intensity = max(50, 255 - int((distance / self.max_range) * 200))
                ray_color = (0, intensity, 100)
                
                pygame.draw.line(
                    surface, ray_color,
                    (robot_x, robot_y),
                    (int(point.x), int(point.y)), 1
                )
    
    def draw_points(self, surface: pygame.Surface, scan: LidarScan, 
                   color: tuple = (0, 255, 0), radius: int = 2) -> None:
        """
        Визуализация точек лидара.
        
        Args:
            surface: поверхность для отрисовки
            scan: результаты сканирования
            color: цвет точек
            radius: радиус точек
        """
        for point in scan.points:
            pygame.draw.circle(surface, color, (int(point.x), int(point.y)), radius)
    
    @classmethod
    def from_config(cls, config: dict):
        """
        Создает лидар из конфигурации.
        
        Args:
            config: словарь с параметрами лидара
            
        Returns:
            Экземпляр Lidar
        """
        lidar_config = config.get('lidar', {})
        
        return cls(
            num_rays=lidar_config.get('num_rays', 360),
            max_range=lidar_config.get('max_range', 300.0),
            fov=lidar_config.get('fov', 360.0),
            noise_std=lidar_config.get('noise_std', 1.0),
            angle_resolution=lidar_config.get('angle_resolution', 1.0)
        )
