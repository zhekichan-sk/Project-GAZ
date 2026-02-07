"""
Режим локализации.
"""

import pygame
from src.gui.modes.base_mode import BaseMode
from src.common.types import SimulationMode
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
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Обрабатывает событие."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_l:
                # Загрузить карту
                print("Загрузка карты...")
                # TODO: реализовать загрузку карты
    
    def update(self, dt: float, keys: pygame.key.ScancodeWrapper) -> None:
        """Обновляет состояние режима."""
        # Локализация выполняется автоматически
        if self.show_lidar:
            self.last_scan = self.lidar.scan(self.robot, self.environment)
            # TODO: выполнить локализацию
            self.estimated_pose = self.robot.pose
            self.confidence = 0.95  # Заглушка
    
    def render(self, screen: pygame.Surface) -> None:
        """Отрисовывает режим."""
        pass
    
    def on_mouse_click(self, pos: tuple, button: int) -> None:
        """Обрабатывает клик мыши."""
        if button == 3:  # ПКМ - телепортация робота
            self.robot.set_position(pos[0], pos[1])

