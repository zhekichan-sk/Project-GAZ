"""
Режим навигации.
"""

import pygame
from typing import Optional, List
from src.gui.modes.base_mode import BaseMode
from src.common.types import SimulationMode, Point
from src.simulation.robot import Robot
from src.simulation.environment import Environment


class NavigationMode(BaseMode):
    """Режим навигации с планированием пути."""
    
    def __init__(self, robot: Robot, environment: Environment):
        super().__init__(SimulationMode.NAVIGATION)
        self.robot = robot
        self.environment = environment
        self.goal: Optional[Point] = None
        self.path: List[Point] = []
        self.auto_move = False
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Обрабатывает событие."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_l:
                # Загрузить карту
                print("Загрузка карты...")
                # TODO: реализовать загрузку карты
    
    def update(self, dt: float, keys: pygame.key.ScancodeWrapper) -> None:
        """Обновляет состояние режима."""
        # TODO: автоматическое движение по пути
        pass
    
    def render(self, screen: pygame.Surface) -> None:
        """Отрисовывает режим."""
        pass
    
    def on_mouse_click(self, pos: tuple, button: int) -> None:
        """Обрабатывает клик мыши."""
        if button == 1:  # ЛКМ - установка цели
            self.goal = Point(pos[0], pos[1])
            # TODO: планирование пути через A*
            self.path = [self.goal]  # Заглушка
            print(f"Цель установлена: ({pos[0]}, {pos[1]})")

