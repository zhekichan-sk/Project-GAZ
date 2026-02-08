"""
Режим редактирования карты (как в map.py / КуМир Стандарт).
"""

import pygame
import math
from src.gui.modes.base_mode import BaseMode
from src.common.types import SimulationMode, Point
from src.simulation.environment import Environment
from src.simulation.obstacles import RectangleObstacle


class MapEditorMode(BaseMode):
    """Режим редактирования карты с размещением препятствий."""
    
    def __init__(self, environment: Environment):
        super().__init__(SimulationMode.MAPPING)
        self.environment = environment
        
        # Параметры сетки
        self.GRID_SIZE = 100
        self.GRID_START_X = 200
        self.GRID_START_Y = 100
        self.GRID_END_X = 1200
        self.GRID_END_Y = 1100
        self.PLACEMENT_AREA_WIDTH = 15
        
        # Параметры препятствия
        self.OBSTACLE_LENGTH = 100
        self.OBSTACLE_WIDTH = 5
        
        self.hovered_edge = None
    
    def get_hovered_edge(self, mouse_x: float, mouse_y: float):
        """Определяет, на какой границе клетки находится мышь."""
        if not self._is_on_grid(mouse_x, mouse_y):
            return None
        
        # Вертикальные границы
        for x in range(self.GRID_START_X + self.GRID_SIZE, self.GRID_END_X, self.GRID_SIZE):
            if abs(mouse_x - x) < self.PLACEMENT_AREA_WIDTH / 2:
                cell_y = ((mouse_y - self.GRID_START_Y) // self.GRID_SIZE) * self.GRID_SIZE + self.GRID_START_Y
                area_center_y = cell_y + self.GRID_SIZE / 2
                if (self.GRID_START_Y + self.GRID_SIZE / 2 <= area_center_y <= self.GRID_END_Y - self.GRID_SIZE / 2):
                    return ('vertical', x, area_center_y)
        
        # Горизонтальные границы
        for y in range(self.GRID_START_Y + self.GRID_SIZE, self.GRID_END_Y, self.GRID_SIZE):
            if abs(mouse_y - y) < self.PLACEMENT_AREA_WIDTH / 2:
                cell_x = ((mouse_x - self.GRID_START_X) // self.GRID_SIZE) * self.GRID_SIZE + self.GRID_START_X
                area_center_x = cell_x + self.GRID_SIZE / 2
                if (self.GRID_START_X + self.GRID_SIZE / 2 <= area_center_x <= self.GRID_END_X - self.GRID_SIZE / 2):
                    return ('horizontal', area_center_x, y)
        
        return None
    
    def _is_on_grid(self, x: float, y: float) -> bool:
        """Проверяет, находится ли точка на сетке."""
        return (self.GRID_START_X <= x <= self.GRID_END_X and 
                self.GRID_START_Y <= y <= self.GRID_END_Y)
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Обрабатывает событие."""
        pass
    
    def update(self, dt: float, keys: pygame.key.ScancodeWrapper) -> None:
        """Обновляет состояние режима."""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.hovered_edge = self.get_hovered_edge(mouse_x, mouse_y)
    
    def render(self, screen: pygame.Surface) -> None:
        """Отрисовывает режим."""
        # Отрисовка области размещения
        if self.hovered_edge:
            edge_type, edge_x, edge_y = self.hovered_edge
            self._draw_placement_area(screen, edge_type, edge_x, edge_y)
    
    def _draw_placement_area(self, screen: pygame.Surface, edge_type: str, x: float, y: float):
        """Отрисовывает область для размещения препятствия."""
        if edge_type == 'vertical':
            rect_x = int(x - self.PLACEMENT_AREA_WIDTH / 2)
            rect_y = int(y - self.GRID_SIZE / 2)
            surface = pygame.Surface((self.PLACEMENT_AREA_WIDTH, self.GRID_SIZE), pygame.SRCALPHA)
            surface.fill((255, 255, 0, 150))
            screen.blit(surface, (rect_x, rect_y))
            rect = pygame.Rect(rect_x, rect_y, self.PLACEMENT_AREA_WIDTH, self.GRID_SIZE)
            pygame.draw.rect(screen, (200, 200, 0), rect, 2)
        elif edge_type == 'horizontal':
            rect_x = int(x - self.GRID_SIZE / 2)
            rect_y = int(y - self.PLACEMENT_AREA_WIDTH / 2)
            surface = pygame.Surface((self.GRID_SIZE, self.PLACEMENT_AREA_WIDTH), pygame.SRCALPHA)
            surface.fill((255, 255, 0, 150))
            screen.blit(surface, (rect_x, rect_y))
            rect = pygame.Rect(rect_x, rect_y, self.GRID_SIZE, self.PLACEMENT_AREA_WIDTH)
            pygame.draw.rect(screen, (200, 200, 0), rect, 2)
    
    def on_mouse_click(self, pos: tuple, button: int) -> None:
        """Обрабатывает клик мыши."""
        if button == 1:  # ЛКМ - размещение препятствия
            edge_info = self.get_hovered_edge(pos[0], pos[1])
            if edge_info:
                edge_type, edge_x, edge_y = edge_info
                angle = 90.0 if edge_type == 'vertical' else 0.0
                placed_obstacle = RectangleObstacle(
                    edge_x, edge_y,
                    self.OBSTACLE_LENGTH,
                    self.OBSTACLE_WIDTH,
                    angle=angle
                )
                self.environment.obstacles.add_placed_obstacle(placed_obstacle)
        elif button == 3:  # ПКМ - удаление препятствия
            mouse_x, mouse_y = pos
            # Ищем препятствие под курсором
            obstacles_to_remove = []
            for obstacle in self.environment.obstacles.get_placed_obstacles():
                if isinstance(obstacle, RectangleObstacle):
                    if obstacle.contains_point(mouse_x, mouse_y):
                        obstacles_to_remove.append(obstacle)
            
            # Удаляем найденные препятствия
            for obstacle in obstacles_to_remove:
                if obstacle in self.environment.obstacles.get_placed_obstacles():
                    self.environment.obstacles.get_placed_obstacles().remove(obstacle)

