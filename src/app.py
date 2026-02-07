"""
Класс приложения для интеграции всех компонентов.
"""

import os
import sys
import json
from typing import Optional

# Добавляем путь к корню проекта
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

from src.simulation.environment import Environment
from src.simulation.robot import Robot
from src.simulation.lidar import Lidar
from src.simulation.obstacles import Obstacles
from src.mapping.occupancy_grid import OccupancyGrid
from src.mapping.mapper import Mapper
from src.localization.localizer import Localizer
from src.localization.scan_matcher import ScanMatcher
from src.navigation.path_planner import PathPlanner
from src.gui.main_window import MainWindow
from src.common.types import Point
from src.common.config_loader import load_robot_config, load_environment_config


class Application:
    """Главный класс приложения."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Args:
            config_path: путь к конфигурационному файлу
        """
        self.config_path = config_path
        self.environment: Optional[Environment] = None
        self.robot: Optional[Robot] = None
        self.lidar: Optional[Lidar] = None
        self.occupancy_grid: Optional[OccupancyGrid] = None
        self.mapper: Optional[Mapper] = None
        self.localizer: Optional[Localizer] = None
        self.path_planner: Optional[PathPlanner] = None
        self.main_window: Optional[MainWindow] = None
    
    def setup(self) -> None:
        """Инициализация всех модулей."""
        # Загрузка конфигурации
        if self.config_path and os.path.exists(self.config_path):
            env_config = load_environment_config(self.config_path)
            robot_config = load_robot_config(self.config_path)
        else:
            # Используем дефолтные конфиги
            default_env_path = os.path.join(project_root, 'configs', 'default_environment.json')
            default_robot_path = os.path.join(project_root, 'configs', 'robot_config.json')
            
            env_config = load_environment_config(default_env_path) if os.path.exists(default_env_path) else {}
            robot_config = load_robot_config(default_robot_path) if os.path.exists(default_robot_path) else {}
        
        # Инициализация среды
        width = env_config.get('environment', {}).get('width', 1500)
        height = env_config.get('environment', {}).get('height', 1200)
        self.environment = Environment(width, height, Obstacles())
        
        # Инициализация робота
        if robot_config:
            self.robot = Robot.from_config(robot_config)
        else:
            self.robot = Robot(x=400.0, y=300.0, theta=0.0)
        
        # Инициализация лидара
        if robot_config:
            self.lidar = Lidar.from_config(robot_config)
        else:
            self.lidar = Lidar(num_rays=360, max_range=300.0)
        
        # Инициализация карты занятости
        # Разрешение 5 пикселей на ячейку
        grid_width = width // 5
        grid_height = height // 5
        self.occupancy_grid = OccupancyGrid(
            width=grid_width,
            height=grid_height,
            resolution=5.0,
            origin=Point(0, 0)
        )
        
        # Инициализация построителя карты
        self.mapper = Mapper(self.occupancy_grid, self.lidar.max_range)
        
        # Инициализация локализатора
        scan_matcher = ScanMatcher(self.occupancy_grid)
        self.localizer = Localizer(self.occupancy_grid, scan_matcher)
        
        # Инициализация планировщика пути
        self.path_planner = PathPlanner(self.occupancy_grid, self.robot.radius)
    
    def run(self, initial_mode: str = "editor", width: int = 1500, height: int = 1200) -> None:
        """
        Запускает приложение.
        
        Args:
            initial_mode: начальный режим ("editor" или "blind")
            width: ширина окна
            height: высота окна
        """
        if not all([self.environment, self.robot, self.lidar]):
            self.setup()
        
        # Создаем главное окно
        self.main_window = MainWindow(
            width=width,
            height=height,
            title="Симулятор робота с лидаром",
            environment=self.environment,
            robot=self.robot,
            lidar=self.lidar,
            occupancy_grid=self.occupancy_grid,
            mapper=self.mapper,
            localizer=self.localizer,
            path_planner=self.path_planner,
            initial_mode=initial_mode
        )
        
        # Запускаем главный цикл
        self.main_window.run()
    
    def cleanup(self) -> None:
        """Очистка ресурсов."""
        if self.main_window:
            # Очистка выполняется в main_window
            pass

