"""
Базовый класс для режимов работы симулятора.
"""

from abc import ABC, abstractmethod
from typing import Optional
import pygame
from src.common.types import SimulationMode, Point


class BaseMode(ABC):
    """Абстрактный базовый класс для режимов работы."""
    
    def __init__(self, mode: SimulationMode):
        self.mode = mode
    
    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        """Обрабатывает событие."""
        pass
    
    @abstractmethod
    def update(self, dt: float, keys: pygame.key.ScancodeWrapper) -> None:
        """Обновляет состояние режима."""
        pass
    
    @abstractmethod
    def render(self, screen: pygame.Surface) -> None:
        """Отрисовывает режим."""
        pass
    
    def on_enter(self) -> None:
        """Вызывается при входе в режим."""
        pass
    
    def on_exit(self) -> None:
        """Вызывается при выходе из режима."""
        pass
    
    def on_mouse_click(self, pos: tuple, button: int) -> None:
        """Обрабатывает клик мыши."""
        pass

