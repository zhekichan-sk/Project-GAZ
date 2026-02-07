"""
Главное окно приложения.
"""

import pygame
import sys
import os
import time
from typing import Optional

# Устанавливаем кодировку для корректной работы с путями
if sys.platform == 'win32':
    import locale
    try:
        locale.setlocale(locale.LC_ALL, '')
    except:
        pass

# Добавляем путь к корню проекта в sys.path для корректного импорта
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
except:
    current_dir = os.getcwd()

if os.path.basename(current_dir) == 'src':
    project_root = os.path.dirname(current_dir)
else:
    project_root = current_dir

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.common.types import SimulationMode
from src.gui.renderer import Renderer
from src.gui.hud import HUD
from src.gui.modes.map_editor_mode import MapEditorMode
from src.gui.modes.blind_robot_mode import BlindRobotMode
from src.simulation.robot import Robot
from src.simulation.environment import Environment
from src.simulation.lidar import Lidar
from src.simulation.obstacles import Obstacles
from src.mapping.occupancy_grid import OccupancyGrid
from src.mapping.mapper import Mapper
from src.localization.localizer import Localizer
from src.navigation.path_planner import PathPlanner


class AppMode:
    """Режимы приложения."""
    EDITOR = "editor"  # Редактор карты
    BLIND_ROBOT = "blind"  # Слепой робот


class MainWindow:
    """Главное окно приложения."""
    
    def __init__(self, width: int = 1500, height: int = 1200, title: str = "Симулятор робота",
                 environment: Environment = None, robot: Robot = None, lidar: Lidar = None,
                 occupancy_grid: OccupancyGrid = None, mapper: Mapper = None,
                 localizer: Localizer = None, path_planner: PathPlanner = None,
                 initial_mode: str = "editor"):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.running = True
        self.width = width
        self.height = height
        
        # Инициализация компонентов
        self.renderer = Renderer(self.screen)
        self.hud = HUD(self.screen)
        
        # Инициализация симуляции
        self.environment = environment or Environment(width, height, Obstacles())
        self.robot = robot or Robot(x=400.0, y=300.0, theta=0.0)
        self.lidar = lidar or Lidar(num_rays=360, max_range=300.0)
        self.occupancy_grid = occupancy_grid
        self.mapper = mapper
        self.localizer = localizer
        self.path_planner = path_planner
        
        # Режимы приложения
        self.current_app_mode = initial_mode  # "editor" или "blind"
        self.map_editor_mode = MapEditorMode(self.environment)
        self.blind_robot_mode = BlindRobotMode(self.robot, self.environment, self.lidar)
        
        # Кнопки для переключения режимов (левее и ниже)
        self.button_editor_rect = pygame.Rect(10, height - 120, 180, 40)
        self.button_blind_rect = pygame.Rect(10, height - 70, 180, 40)
        
        # Кнопки для сохранения/загрузки карты
        self.button_save_rect = pygame.Rect(10, height - 170, 180, 40)
        self.button_load_rect = pygame.Rect(10, height - 220, 180, 40)
        
        # Флаг выбора позиции робота
        self.selecting_robot_position = False
        self.robot_start_position = None
    
    def run(self) -> None:
        """Главный цикл приложения."""
        last_time = time.time()
        
        while self.running:
            # Вычисление delta time
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            dt = min(dt, 0.1)  # Ограничение максимального dt
            
            # Обработка событий
            self.handle_events()
            
            # Обновление
            self.update(dt)
            
            # Отрисовка
            self.render()
            
            # Ограничение FPS
            self.clock.tick(self.fps)
        
        pygame.quit()
        sys.exit()
    
    def handle_events(self) -> None:
        """Обрабатывает события."""
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_c:
                    # Очистка
                    if self.current_app_mode == AppMode.EDITOR:
                        self.environment.obstacles.clear_placed_obstacles()
                    elif self.current_app_mode == AppMode.BLIND_ROBOT:
                        self.blind_robot_mode.clear_history()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Проверка клика по кнопкам
                if self.button_editor_rect.collidepoint(mouse_pos):
                    self.current_app_mode = AppMode.EDITOR
                elif self.button_blind_rect.collidepoint(mouse_pos):
                    self.current_app_mode = AppMode.BLIND_ROBOT
                    # Сбрасываем историю при переходе в режим слепого робота
                    self.blind_robot_mode.clear_history()
                else:
                    # Передача события текущему режиму
                    if self.current_app_mode == AppMode.EDITOR:
                        self.map_editor_mode.on_mouse_click(mouse_pos, event.button)
            
            elif event.type == pygame.MOUSEMOTION:
                # Обновление режима редактора
                if self.current_app_mode == AppMode.EDITOR:
                    self.map_editor_mode.handle_event(event)
    
    def update(self, dt: float) -> None:
        """Обновляет логику."""
        keys = pygame.key.get_pressed()
        
        if self.current_app_mode == AppMode.EDITOR:
            self.map_editor_mode.update(dt, keys)
        elif self.current_app_mode == AppMode.BLIND_ROBOT:
            self.blind_robot_mode.update(dt, keys)
            
            # Обновление карты занятости
            if self.mapper and self.blind_robot_mode.last_scan:
                self.mapper.update_from_scan(self.blind_robot_mode.last_scan)
    
    def render(self) -> None:
        """Отрисовывает содержимое."""
        # Очистка экрана
        self.screen.fill((255, 255, 255))
        
        if self.selecting_robot_position:
            # Режим выбора позиции робота
            self._render_position_selection_mode()
        elif self.current_app_mode == AppMode.EDITOR:
            # Режим редактора карты
            self._render_editor_mode()
        elif self.current_app_mode == AppMode.BLIND_ROBOT:
            # Режим слепого робота
            self._render_blind_robot_mode()
        
        # Отрисовка кнопок
        self._render_buttons()
        
        # Отрисовка HUD
        info = {'fps': self.clock.get_fps()}
        if self.selecting_robot_position:
            mode_name = "Выбор позиции робота"
        else:
            mode_name = "Редактор карты" if self.current_app_mode == AppMode.EDITOR else "Слепой робот"
        self.hud.render(self.robot, SimulationMode.MAPPING, info)
        
        # Обновление экрана
        pygame.display.flip()
    
    def _render_editor_mode(self) -> None:
        """Отрисовывает режим редактора карты."""
        # Отрисовка сетки
        self._draw_grid()
        
        # Отрисовка размещенных препятствий
        self.renderer.render_environment(self.environment)
        
        # Отрисовка области размещения
        self.map_editor_mode.render(self.screen)
    
    def _render_blind_robot_mode(self) -> None:
        """Отрисовывает режим слепого робота."""
        # Сначала отрисовываем среду (препятствия)
        self.renderer.render_environment(self.environment)
        
        # Отрисовка режима слепого робота (туман войны)
        self.blind_robot_mode.render(self.screen)
        
        # Отрисовка лидара (только зеленые точки)
        if self.blind_robot_mode.last_scan:
            self.renderer.render_lidar_scan(
                self.blind_robot_mode.last_scan,
                "points"
            )
        
        # Отрисовка робота
        self.renderer.render_robot(self.robot)
        
        # Отрисовка траектории
        if self.robot.trajectory:
            self.renderer.render_trajectory(self.robot.trajectory)
    
    def _draw_grid(self) -> None:
        """Отрисовывает сетку."""
        GRID_SIZE = 100
        GRID_START_X = 200
        GRID_START_Y = 100
        GRID_END_X = 1200
        GRID_END_Y = 1100
        
        for x in range(GRID_START_X, GRID_END_X + 1, GRID_SIZE):
            pygame.draw.line(
                self.screen, (200, 200, 200),
                (x, GRID_START_Y), (x, GRID_END_Y), 1
            )
        for y in range(GRID_START_Y, GRID_END_Y + 1, GRID_SIZE):
            pygame.draw.line(
                self.screen, (200, 200, 200),
                (GRID_START_X, y), (GRID_END_X, y), 1
            )
    
    def _render_position_selection_mode(self) -> None:
        """Отрисовывает режим выбора позиции робота."""
        # Отрисовываем среду
        self._draw_grid()
        self.renderer.render_environment(self.environment)
        
        # Отрисовываем курсор как предпросмотр позиции робота
        mouse_x, mouse_y = pygame.mouse.get_pos()
        from src.common.types import Point
        is_valid = self.environment.is_valid_position(Point(mouse_x, mouse_y), self.robot.radius)
        
        # Цвет зависит от валидности позиции
        preview_color = (0, 255, 0) if is_valid else (255, 0, 0)
        pygame.draw.circle(self.screen, preview_color, (mouse_x, mouse_y), int(self.robot.radius))
        pygame.draw.circle(self.screen, (0, 0, 0), (mouse_x, mouse_y), int(self.robot.radius), 2)
        
        # Инструкция
        font = pygame.font.Font(None, 36)
        instruction = font.render("Выберите начальную позицию робота (ЛКМ)", True, (0, 0, 0))
        self.screen.blit(instruction, (self.width // 2 - instruction.get_width() // 2, 50))
    
    def _render_buttons(self) -> None:
        """Отрисовывает все кнопки."""
        font = pygame.font.Font(None, 28)
        
        # Кнопка сохранения карты
        save_color = (100, 150, 255)
        pygame.draw.rect(self.screen, save_color, self.button_save_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), self.button_save_rect, 2)
        save_text = font.render("Сохранить карту", True, (0, 0, 0))
        text_rect = save_text.get_rect(center=self.button_save_rect.center)
        self.screen.blit(save_text, text_rect)
        
        # Кнопка загрузки карты
        load_color = (150, 100, 255)
        pygame.draw.rect(self.screen, load_color, self.button_load_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), self.button_load_rect, 2)
        load_text = font.render("Загрузить карту", True, (0, 0, 0))
        text_rect = load_text.get_rect(center=self.button_load_rect.center)
        self.screen.blit(load_text, text_rect)
        
        # Кнопка редактора
        editor_color = (100, 200, 100) if self.current_app_mode == AppMode.EDITOR else (150, 150, 150)
        pygame.draw.rect(self.screen, editor_color, self.button_editor_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), self.button_editor_rect, 2)
        editor_text = font.render("Редактор карты", True, (0, 0, 0))
        text_rect = editor_text.get_rect(center=self.button_editor_rect.center)
        self.screen.blit(editor_text, text_rect)
        
        # Кнопка слепого робота
        blind_color = (200, 100, 100) if self.current_app_mode == AppMode.BLIND_ROBOT else (150, 150, 150)
        pygame.draw.rect(self.screen, blind_color, self.button_blind_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), self.button_blind_rect, 2)
        blind_text = font.render("Слепой робот", True, (0, 0, 0))
        text_rect = blind_text.get_rect(center=self.button_blind_rect.center)
        self.screen.blit(blind_text, text_rect)
    
    def _save_map(self) -> None:
        """Сохраняет карту (препятствия) в файл."""
        import os
        import pickle
        import tkinter as tk
        from tkinter import filedialog
        
        # Используем диалог выбора файла
        root = tk.Tk()
        root.withdraw()  # Скрываем главное окно
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pkl",
            filetypes=[("Pickle files", "*.pkl"), ("All files", "*.*")],
            initialdir=os.path.join(project_root, "maps"),
            title="Сохранить карту"
        )
        
        root.destroy()
        
        if file_path:
            try:
                # Создаем директорию если не существует
                maps_dir = os.path.dirname(file_path) if os.path.dirname(file_path) else "maps"
                os.makedirs(maps_dir, exist_ok=True)
                
                # Сохраняем препятствия
                obstacles_data = []
                for obstacle in self.environment.obstacles.get_placed_obstacles():
                    obstacles_data.append({
                        'x': obstacle.x,
                        'y': obstacle.y,
                        'width': obstacle.width,
                        'height': obstacle.height,
                        'angle': obstacle.angle
                    })
                
                map_data = {
                    'obstacles': obstacles_data,
                    'width': self.width,
                    'height': self.height
                }
                
                with open(file_path, 'wb') as f:
                    pickle.dump(map_data, f)
                
                print(f"Карта сохранена в {file_path}")
            except Exception as e:
                print(f"Ошибка при сохранении карты: {e}")
    
    def _load_map(self) -> None:
        """Загружает карту (препятствия) из файла."""
        import os
        import pickle
        import tkinter as tk
        from tkinter import filedialog
        from src.simulation.obstacles import RectangleObstacle
        
        # Используем диалог выбора файла
        root = tk.Tk()
        root.withdraw()
        
        file_path = filedialog.askopenfilename(
            filetypes=[("Pickle files", "*.pkl"), ("All files", "*.*")],
            initialdir=os.path.join(project_root, "maps"),
            title="Загрузить карту"
        )
        
        root.destroy()
        
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, 'rb') as f:
                    map_data = pickle.load(f)
                
                # Очищаем текущие препятствия
                self.environment.obstacles.clear_placed_obstacles()
                
                # Загружаем препятствия
                for obs_data in map_data.get('obstacles', []):
                    obstacle = RectangleObstacle(
                        obs_data['x'],
                        obs_data['y'],
                        obs_data['width'],
                        obs_data['height'],
                        angle=obs_data.get('angle', 0.0)
                    )
                    self.environment.obstacles.add_placed_obstacle(obstacle)
                
                print(f"Карта загружена из {file_path} ({len(map_data.get('obstacles', []))} препятствий)")
            except Exception as e:
                print(f"Ошибка при загрузке карты: {e}")
                import traceback
                traceback.print_exc()


def main():
    """Точка входа в приложение."""
    window = MainWindow()
    window.run()


if __name__ == "__main__":
    main()
