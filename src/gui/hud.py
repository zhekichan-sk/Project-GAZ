"""
Панель управления (HUD) для отображения информации.
"""

import pygame
from typing import Dict, Optional
from src.common.types import SimulationMode
from src.simulation.robot import Robot


class HUD:
    """Панель управления для отображения информации."""
    
    def __init__(self, screen: pygame.Surface, font_size: int = 24):
        self.screen = screen
        self.font = pygame.font.Font(None, font_size)
        self.small_font = pygame.font.Font(None, 18)
        self.colors = {
            'black': (0, 0, 0),
            'white': (255, 255, 255),
            'blue': (0, 0, 255),
            'green': (0, 255, 0),
            'red': (255, 0, 0),
            'yellow': (255, 255, 0),
        }
    
    def render(self, robot: Robot, mode: SimulationMode, info: Dict = None) -> None:
        """Отрисовывает HUD."""
        if info is None:
            info = {}
        
        y_offset = 10
        x_offset = 10
        
        # Текущий режим
        mode_text = f"Режим: {mode.value.upper()}"
        mode_surface = self.font.render(mode_text, True, self.colors['blue'])
        self.screen.blit(mode_surface, (x_offset, y_offset))
        y_offset += 30
        
        # Позиция робота
        robot_text = f"Робот: x={robot.pose.x:.1f}, y={robot.pose.y:.1f}, θ={robot.pose.theta:.2f}"
        robot_surface = self.font.render(robot_text, True, self.colors['black'])
        self.screen.blit(robot_surface, (x_offset, y_offset))
        y_offset += 30
        
        # FPS
        if 'fps' in info:
            fps_text = f"FPS: {info['fps']:.1f}"
            fps_surface = self.font.render(fps_text, True, self.colors['black'])
            self.screen.blit(fps_surface, (x_offset, y_offset))
            y_offset += 30
        
        # Прогресс картографирования
        if 'mapping_progress' in info:
            progress_text = f"Карта: {info['mapping_progress']:.1f}%"
            progress_surface = self.font.render(progress_text, True, self.colors['green'])
            self.screen.blit(progress_surface, (x_offset, y_offset))
            y_offset += 30
        
        # Статус локализации
        if 'localization_confidence' in info:
            conf_text = f"Уверенность: {info['localization_confidence']:.2f}"
            conf_surface = self.font.render(conf_text, True, self.colors['yellow'])
            self.screen.blit(conf_surface, (x_offset, y_offset))
            y_offset += 30
        
        # Длина пути
        if 'path_length' in info:
            path_text = f"Длина пути: {info['path_length']:.1f}"
            path_surface = self.font.render(path_text, True, self.colors['green'])
            self.screen.blit(path_surface, (x_offset, y_offset))
            y_offset += 30
        
        # Подсказки по управлению (внизу экрана)
        self._render_controls_hint()
    
    def _render_controls_hint(self) -> None:
        """Отрисовывает подсказки по управлению."""
        screen_height = self.screen.get_height()
        y_offset = screen_height - 150
        
        hints = [
            "Управление:",
            "W/↑, S/↓, A/←, D/→ - движение",
            "1, 2, 3 - переключение режимов",
            "R - сброс позиции",
            "C - очистка",
            "M - сохранить карту",
            "L - загрузить карту",
            "ESC - выход"
        ]
        
        for i, hint in enumerate(hints):
            color = self.colors['blue'] if i == 0 else self.colors['black']
            hint_surface = self.small_font.render(hint, True, color)
            self.screen.blit(hint_surface, (10, y_offset + i * 18))

