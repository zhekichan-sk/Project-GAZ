"""
Панель управления (HUD) для отображения информации.
"""

import pygame
from typing import Dict, Optional
from src.common.types import SimulationMode
from src.simulation.robot import Robot


class HUD:
    """Панель управления для отображения информации."""
    
    def __init__(self, screen: pygame.Surface, font_size: int = 32):
        self.screen = screen
        self.font = pygame.font.Font(None, font_size)
        self.small_font = pygame.font.Font(None, 22)
        self.colors = {
            'black': (0, 0, 0),
            'white': (255, 255, 255),
            'blue': (0, 0, 255),
            'green': (0, 255, 0),
            'red': (255, 0, 0),
            'yellow': (255, 255, 0),
        }
    
    def _get_text_color(self, x: int, y: int) -> tuple:
        """Определяет цвет текста в зависимости от фона (черный на белом, белый на черном)."""
        # Текст размещается слева от сетки (X < 400), где обычно белый фон
        # Но проверяем цвет пикселя для точности
        try:
            # Берем несколько пикселей вокруг для более точного определения
            sample_points = [(x, y), (x + 5, y), (x, y + 5)]
            total_brightness = 0
            count = 0
            
            for px, py in sample_points:
                try:
                    pixel_color = self.screen.get_at((px, py))
                    # Яркость = среднее значение RGB
                    brightness = sum(pixel_color[:3]) / 3
                    total_brightness += brightness
                    count += 1
                except:
                    pass
            
            if count > 0:
                avg_brightness = total_brightness / count
                # Если средняя яркость < 128 (темный фон), используем белый текст
                if avg_brightness < 128:
                    return self.colors['white']
            
            # По умолчанию черный текст (для белого фона)
            return self.colors['black']
        except:
            # По умолчанию черный текст
            return self.colors['black']
    
    def render(self, robot: Robot, mode: SimulationMode, info: Dict = None) -> None:
        """Отрисовывает HUD."""
        if info is None:
            info = {}
        
        y_offset = 10
        x_offset = 10  # Слева от сетки (сетка начинается с X=400)
        
        # Текущий режим
        mode_text = f"Режим: {mode.value.upper()}"
        text_color = self._get_text_color(x_offset, y_offset)
        mode_surface = self.font.render(mode_text, True, text_color)
        self.screen.blit(mode_surface, (x_offset, y_offset))
        y_offset += 35
        
        # Позиция робота
        robot_text = f"Робот: x={robot.pose.x:.1f}, y={robot.pose.y:.1f}, θ={robot.pose.theta:.2f}"
        text_color = self._get_text_color(x_offset, y_offset)
        robot_surface = self.font.render(robot_text, True, text_color)
        self.screen.blit(robot_surface, (x_offset, y_offset))
        y_offset += 35
        
        # FPS
        if 'fps' in info:
            fps_text = f"FPS: {info['fps']:.1f}"
            text_color = self._get_text_color(x_offset, y_offset)
            fps_surface = self.font.render(fps_text, True, text_color)
            self.screen.blit(fps_surface, (x_offset, y_offset))
            y_offset += 35
        
        # Прогресс картографирования
        if 'mapping_progress' in info:
            progress_text = f"Карта: {info['mapping_progress']:.1f}%"
            text_color = self._get_text_color(x_offset, y_offset)
            progress_surface = self.font.render(progress_text, True, text_color)
            self.screen.blit(progress_surface, (x_offset, y_offset))
            y_offset += 35
        
        # Статус локализации
        if 'localization_confidence' in info:
            conf_text = f"Уверенность: {info['localization_confidence']:.2f}"
            text_color = self._get_text_color(x_offset, y_offset)
            conf_surface = self.font.render(conf_text, True, text_color)
            self.screen.blit(conf_surface, (x_offset, y_offset))
            y_offset += 35
        
        # Длина пути
        if 'path_length' in info:
            path_text = f"Длина пути: {info['path_length']:.1f}"
            text_color = self._get_text_color(x_offset, y_offset)
            path_surface = self.font.render(path_text, True, text_color)
            self.screen.blit(path_surface, (x_offset, y_offset))
            y_offset += 35
        
        # Подсказки по управлению (внизу экрана)
        self._render_controls_hint()
    
    def _render_controls_hint(self) -> None:
        """Отрисовывает подсказки по управлению."""
        screen_height = self.screen.get_height()
        screen_width = self.screen.get_width()
        y_offset = screen_height - 180
        x_offset = 10  # Слева от сетки
        
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
            text_color = self._get_text_color(x_offset, y_offset + i * 22)
            hint_surface = self.small_font.render(hint, True, text_color)
            self.screen.blit(hint_surface, (x_offset, y_offset + i * 22))

