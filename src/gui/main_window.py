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
from src.gui.modes.mapping_mode import MappingMode
from src.gui.modes.localization_mode import LocalizationMode
from src.gui.modes.navigation_mode import NavigationMode
from src.simulation.robot import Robot
from src.simulation.environment import Environment
from src.simulation.lidar import Lidar
from src.simulation.obstacles import Obstacles
from src.mapping.occupancy_grid import OccupancyGrid
from src.mapping.mapper import Mapper
from src.localization.localizer import Localizer
from src.navigation.path_planner import PathPlanner
from src.common.types import Point
import random
import math


class AppMode:
    """Режимы приложения."""
    EDITOR = "editor"  # Редактор карты
    BLIND_ROBOT = "blind"  # Слепой робот
    MAPPING = "mapping"  # Картографирование
    LOCALIZATION = "localization"  # Локализация
    NAVIGATION = "navigation"  # Навигация


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
        env = self.environment
        robot_x = (env.grid_left + env.grid_right) / 2
        robot_y = (env.grid_top + env.grid_bottom) / 2
        self.robot = robot or Robot(x=robot_x, y=robot_y, theta=0.0)
        self.lidar = lidar or Lidar(num_rays=360, max_range=300.0)
        self.occupancy_grid = occupancy_grid
        self.mapper = mapper
        self.localizer = localizer
        self.path_planner = path_planner
        
        # Режимы приложения
        self.current_app_mode = initial_mode  # "editor", "blind", "mapping", "localization"
        self.map_editor_mode = MapEditorMode(self.environment)
        self.blind_robot_mode = BlindRobotMode(self.robot, self.environment, self.lidar)
        self.mapping_mode = MappingMode(self.robot, self.environment, self.lidar)
        self.localization_mode = LocalizationMode(self.robot, self.environment, self.lidar)
        self.navigation_mode = NavigationMode(self.robot, self.environment)
        
        # Для режима локализации - оцененная позиция
        self.estimated_pose = None
        self.localization_confidence = 0.0
        self._localization_frame_counter = 0  # Локализация раз в N кадров
        
        # Если начальный режим - картографирование, размещаем робота в случайной клетке
        if self.current_app_mode == AppMode.MAPPING and self.occupancy_grid:
            self._reset_mapping_mode()
        
        # Кнопки (только редактор, сохранение, загрузка; режимы 1, 2, 3 — по клавишам)
        self.button_editor_rect = pygame.Rect(width - 200, height - 120, 180, 40)
        self.button_save_rect = pygame.Rect(width - 200, height - 170, 180, 40)
        self.button_load_rect = pygame.Rect(width - 200, height - 220, 180, 40)
        
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
                elif event.key == pygame.K_1:
                    # Режим картографирования (робот остаётся на месте)
                    self.current_app_mode = AppMode.MAPPING
                elif event.key == pygame.K_2:
                    # Режим локализации
                    self.current_app_mode = AppMode.LOCALIZATION
                    self._reset_localization_mode()
                elif event.key == pygame.K_3:
                    # Режим навигации
                    self.current_app_mode = AppMode.NAVIGATION
                elif event.key == pygame.K_c:
                    # Очистка
                    if self.current_app_mode == AppMode.EDITOR:
                        self.environment.obstacles.clear_placed_obstacles()
                    elif self.current_app_mode == AppMode.MAPPING:
                        if self.occupancy_grid and self.mapper:
                            self.mapper.reset()
                            self._reset_mapping_mode()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Проверка клика по кнопкам
                if self.button_save_rect.collidepoint(mouse_pos):
                    self._save_map()
                elif self.button_load_rect.collidepoint(mouse_pos):
                    self._load_map()
                elif self.button_editor_rect.collidepoint(mouse_pos):
                    self.current_app_mode = AppMode.EDITOR
                else:
                    # Передача события текущему режиму
                    if self.current_app_mode == AppMode.EDITOR:
                        self.map_editor_mode.on_mouse_click(mouse_pos, event.button)
                    elif self.current_app_mode == AppMode.NAVIGATION and event.button == 1:
                        # ЛКМ — установка цели и построение пути
                        if self.path_planner and self.occupancy_grid:
                            found = self.navigation_mode.set_goal(
                                mouse_pos, self.path_planner, self.occupancy_grid
                            )
                            if found:
                                print(f"Путь найден, длина: {self.navigation_mode.path_length:.1f}")
                            else:
                                print("Путь не найден или цель недоступна")
            
            elif event.type == pygame.MOUSEMOTION:
                # Обновление режима редактора
                if self.current_app_mode == AppMode.EDITOR:
                    self.map_editor_mode.handle_event(event)
    
    def update(self, dt: float) -> None:
        """Обновляет логику."""
        keys = pygame.key.get_pressed()
        
        if self.current_app_mode == AppMode.EDITOR:
            self.map_editor_mode.update(dt, keys)
        elif self.current_app_mode == AppMode.MAPPING:
            self.mapping_mode.update(dt, keys)
            
            # Обновление карты занятости на основе сканов лидара
            if self.mapper and self.mapping_mode.last_scan:
                self.mapper.update_from_scan(self.mapping_mode.last_scan)
        elif self.current_app_mode == AppMode.LOCALIZATION:
            self.localization_mode.update(dt, keys)
        elif self.current_app_mode == AppMode.NAVIGATION:
            self.navigation_mode.update(dt, keys)
            
            # Локализация раз в 15 кадров (для производительности)
            self._localization_frame_counter += 1
            if (self.localizer and self.localization_mode.last_scan and self.occupancy_grid
                    and self._localization_frame_counter >= 15):
                self._localization_frame_counter = 0
                odometry_pose = self.robot.get_odometry()
                result = self.localizer.localize(self.localization_mode.last_scan, odometry_pose)
                self.estimated_pose = Point(result.pose.x, result.pose.y)
                self.localization_confidence = result.confidence
    
    def render(self) -> None:
        """Отрисовывает содержимое."""
        # Очистка экрана
        self.screen.fill((255, 255, 255))
        
        if self.selecting_robot_position:
            # Режим выбора позиции робота
            self._render_position_selection_mode()
        elif self.current_app_mode == AppMode.EDITOR:
            self._render_editor_mode()
        elif self.current_app_mode == AppMode.MAPPING:
            # Режим картографирования
            self._render_mapping_mode()
        elif self.current_app_mode == AppMode.LOCALIZATION:
            self._render_localization_mode()
        elif self.current_app_mode == AppMode.NAVIGATION:
            self._render_navigation_mode()
        
        # Отрисовка кнопок
        self._render_buttons()
        
        # Отрисовка мини-карты (если есть карта занятости)
        if self.occupancy_grid and self.current_app_mode in [AppMode.MAPPING, AppMode.LOCALIZATION, AppMode.NAVIGATION]:
            robot_point = Point(self.robot.pose.x, self.robot.pose.y)
            estimated_point = self.estimated_pose if self.current_app_mode == AppMode.LOCALIZATION else None
            self.renderer.render_minimap(
                self.occupancy_grid,
                robot_pose=robot_point,
                estimated_pose=estimated_point,
                size=200,
                position=(self.width - 210, 10)
            )
        
        # Отрисовка HUD
        info = {'fps': self.clock.get_fps()}
        if self.selecting_robot_position:
            mode_name = "Выбор позиции робота"
        elif self.current_app_mode == AppMode.MAPPING:
            mode_name = "Картографирование"
            if self.mapper:
                info['mapping_progress'] = self.mapper.get_completion_percentage()
        elif self.current_app_mode == AppMode.LOCALIZATION:
            mode_name = "Локализация"
            info['localization_confidence'] = self.localization_confidence
        elif self.current_app_mode == AppMode.NAVIGATION:
            mode_name = "Навигация"
            if self.navigation_mode.path_found:
                info['path_length'] = self.navigation_mode.path_length
        else:
            mode_name = "Редактор карты"

        sim_mode = SimulationMode.MAPPING if self.current_app_mode == AppMode.MAPPING else \
                   SimulationMode.LOCALIZATION if self.current_app_mode == AppMode.LOCALIZATION else \
                   SimulationMode.NAVIGATION if self.current_app_mode == AppMode.NAVIGATION else \
                   SimulationMode.MAPPING
        self.hud.render(self.robot, sim_mode, info)
        
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
        # Среда без границ (границы рисуем поверх тумана)
        self.renderer.render_environment(self.environment, draw_boundaries=False)
        
        # Отрисовка режима слепого робота (туман войны)
        self.blind_robot_mode.render(self.screen)
        
        # Жёлтые границы поверх тумана (всегда видны)
        self.renderer.render_boundary_obstacles(self.environment)
        
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
    
    def _render_mapping_mode(self) -> None:
        """Отрисовывает режим картографирования."""
        # Отрисовка сетки
        self._draw_grid()
        
        # Отрисовка среды (препятствия)
        self.renderer.render_environment(self.environment)
        
        # Отрисовка карты занятости (полупрозрачно)
        if self.occupancy_grid:
            self.renderer.render_occupancy_grid(self.occupancy_grid, alpha=128)
        
        # Отрисовка лидара
        if self.mapping_mode.last_scan:
            self.renderer.render_lidar_scan(
                self.mapping_mode.last_scan,
                "points"
            )
        
        # Отрисовка робота
        self.renderer.render_robot(self.robot)
        
        # Отрисовка траектории
        if self.robot.trajectory:
            self.renderer.render_trajectory(self.robot.trajectory)
    
    def _render_localization_mode(self) -> None:
        """Отрисовывает режим локализации."""
        self._draw_grid()
        self.renderer.render_environment(self.environment)
        self.renderer.render_robot(self.robot)
        if self.robot.trajectory:
            self.renderer.render_trajectory(self.robot.trajectory)
    
    def _render_navigation_mode(self) -> None:
        """Отрисовывает режим навигации."""
        self._draw_grid()
        self.renderer.render_environment(self.environment)
        
        # Карта занятости (полупрозрачно)
        if self.occupancy_grid:
            self.renderer.render_occupancy_grid(self.occupancy_grid, alpha=128)
        
        # Путь — красная линия от текущей позиции робота до цели
        if self.navigation_mode.path:
            path_with_start = [Point(self.robot.pose.x, self.robot.pose.y)] + list(self.navigation_mode.path)
            self.renderer.render_path(path_with_start, color=(255, 0, 0))
        
        # Цель (красный круг)
        if self.navigation_mode.goal:
            self.renderer.render_goal(self.navigation_mode.goal)
        
        self.renderer.render_robot(self.robot)
        if self.robot.trajectory:
            self.renderer.render_trajectory(self.robot.trajectory)
    
    def _reset_mapping_mode(self) -> None:
        """Сбрасывает режим картографирования и размещает робота в случайной клетке."""
        if not self.occupancy_grid:
            return
        
        # Размещаем робота в центре случайной клетки
        # Получаем случайные индексы ячейки
        random_i = random.randint(0, self.occupancy_grid.height - 1)
        random_j = random.randint(0, self.occupancy_grid.width - 1)
        
        # Преобразуем в мировые координаты (центр ячейки)
        world_point = self.occupancy_grid.grid_to_world(random_i, random_j)
        
        # Проверяем, что позиция валидна
        if self.environment.is_valid_position(world_point, self.robot.radius):
            self.robot.set_position(world_point.x, world_point.y, random.uniform(0, 2 * math.pi))
            self.robot.clear_trajectory()
        else:
            # Если позиция невалидна, пробуем другую
            for _ in range(10):  # Максимум 10 попыток
                random_i = random.randint(0, self.occupancy_grid.height - 1)
                random_j = random.randint(0, self.occupancy_grid.width - 1)
                world_point = self.occupancy_grid.grid_to_world(random_i, random_j)
                if self.environment.is_valid_position(world_point, self.robot.radius):
                    self.robot.set_position(world_point.x, world_point.y, random.uniform(0, 2 * math.pi))
                    self.robot.clear_trajectory()
                    break
    
    def _reset_localization_mode(self) -> None:
        """Сбрасывает режим локализации и телепортирует робота в случайное место."""
        if not self.occupancy_grid:
            return
        
        # Телепортируем робота в случайное место
        random_i = random.randint(0, self.occupancy_grid.height - 1)
        random_j = random.randint(0, self.occupancy_grid.width - 1)
        world_point = self.occupancy_grid.grid_to_world(random_i, random_j)
        
        # Проверяем, что позиция валидна
        if self.environment.is_valid_position(world_point, self.robot.radius):
            self.robot.set_position(world_point.x, world_point.y, random.uniform(0, 2 * math.pi))
            self.robot.clear_trajectory()
            # Сбрасываем оцененную позицию
            self.estimated_pose = None
            self.localization_confidence = 0.0
            self._localization_frame_counter = 15  # Сразу запустить локализацию
        else:
            # Если позиция невалидна, пробуем другую
            for _ in range(10):  # Максимум 10 попыток
                random_i = random.randint(0, self.occupancy_grid.height - 1)
                random_j = random.randint(0, self.occupancy_grid.width - 1)
                world_point = self.occupancy_grid.grid_to_world(random_i, random_j)
                if self.environment.is_valid_position(world_point, self.robot.radius):
                    self.robot.set_position(world_point.x, world_point.y, random.uniform(0, 2 * math.pi))
                    self.robot.clear_trajectory()
                    self.estimated_pose = None
                    self.localization_confidence = 0.0
                    self._localization_frame_counter = 15
                    break
    
    def _draw_grid(self) -> None:
        """Отрисовывает сетку."""
        env = self.environment
        gs = env.GRID_SIZE
        for x in range(env.grid_left, env.grid_right + 1, gs):
            pygame.draw.line(
                self.screen, (200, 200, 200),
                (x, env.grid_top), (x, env.grid_bottom), 1
            )
        for y in range(env.grid_top, env.grid_bottom + 1, gs):
            pygame.draw.line(
                self.screen, (200, 200, 200),
                (env.grid_left, y), (env.grid_right, y), 1
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
        
        # Инструкция (слева от сетки, чтобы не залезала на нее)
        font = pygame.font.Font(None, 40)
        instruction = font.render("Выберите начальную позицию робота (ЛКМ)", True, (0, 0, 0))
        # Размещаем слева от сетки (сетка начинается с X=400)
        self.screen.blit(instruction, (50, 50))
    
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
    
    def _save_map(self) -> None:
        """Сохраняет карту (препятствия) в файл."""
        import os
        import pickle
        import tkinter as tk
        from tkinter import filedialog
        
        # Определяем путь к папке Maps
        maps_dir = os.path.join(project_root, "Maps")
        os.makedirs(maps_dir, exist_ok=True)
        
        # Используем диалог выбора файла
        root = tk.Tk()
        root.withdraw()  # Скрываем главное окно
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pkl",
            filetypes=[("Pickle files", "*.pkl"), ("All files", "*.*")],
            initialdir=maps_dir,
            title="Сохранить карту"
        )
        
        root.destroy()
        
        if file_path:
            try:
                # Убеждаемся, что файл сохраняется в папку Maps
                if not file_path.startswith(maps_dir):
                    # Если пользователь выбрал другую папку, используем Maps
                    filename = os.path.basename(file_path)
                    file_path = os.path.join(maps_dir, filename)
                
                # Создаем директорию если не существует
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
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
        
        # Определяем путь к папке Maps
        maps_dir = os.path.join(project_root, "Maps")
        os.makedirs(maps_dir, exist_ok=True)
        
        # Используем диалог выбора файла
        root = tk.Tk()
        root.withdraw()
        
        file_path = filedialog.askopenfilename(
            filetypes=[("Pickle files", "*.pkl"), ("All files", "*.*")],
            initialdir=maps_dir,
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
