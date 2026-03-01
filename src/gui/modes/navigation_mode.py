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
    """Режим навигации с планированием пути (муравьиные колонии)."""
    
    def __init__(self, robot: Robot, environment: Environment):
        super().__init__(SimulationMode.NAVIGATION)
        self.robot = robot
        self.environment = environment
        self.goal: Optional[Point] = None
        self.path: List[Point] = []
        self.path_length: float = 0.0
        self.path_found: bool = False
        self.auto_move = False
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Обрабатывает событие."""
        pass
    
    def update(self, dt: float, keys: pygame.key.ScancodeWrapper) -> None:
        """Обновляет состояние режима."""
        pass
    
    def render(self, screen: pygame.Surface) -> None:
        """Отрисовывает режим."""
        pass
    
    def set_goal(self, pos: tuple, path_planner, occupancy_grid) -> bool:
        """
        Устанавливает цель и строит путь алгоритмом муравьиных колоний.
        
        Returns:
            True если путь найден
        """
        if not path_planner or not occupancy_grid:
            return False
        
        goal = Point(pos[0], pos[1])
        env = self.environment
        
        # Проверка: цель в пределах сетки
        if (goal.x < env.grid_left or goal.x > env.grid_right or
            goal.y < env.grid_top or goal.y > env.grid_bottom):
            return False
        
        # Проверка: цель не на препятствии
        if not env.is_valid_position(goal, self.robot.radius):
            return False
        
        self.goal = goal
        start = Point(self.robot.pose.x, self.robot.pose.y)
        
        result = path_planner.plan(start, goal)
        self.path_found = result.found
        self.path = result.path if result.found else []
        self.path_length = result.length if result.found else 0.0
        
        return result.found
    
    def on_mouse_click(self, pos: tuple, button: int) -> None:
        """Обрабатывает клик мыши (вызов set_goal из MainWindow)."""
        pass
    
    def clear_goal(self) -> None:
        """Сбрасывает цель и путь."""
        self.goal = None
        self.path = []
        self.path_length = 0.0
        self.path_found = False

