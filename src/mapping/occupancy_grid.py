"""
Карта занятости (Occupancy Grid).
"""

import numpy as np
import pickle
from typing import Tuple, List
from src.common.types import Point
from .bresenham import bresenham_line


class OccupancyGrid:
    """Карта занятости для представления среды."""
    
    def __init__(self, width: int, height: int, resolution: float, origin: Point):
        """
        Args:
            width: ширина в ячейках
            height: высота в ячейках
            resolution: размер ячейки в единицах (например, 5 = 5x5 пикселей)
            origin: координаты левого нижнего угла в мировых координатах
        """
        self.width = width
        self.height = height
        self.resolution = resolution
        self.origin = origin
        
        # 2D массив вероятностей [0.0, 1.0]
        # 0.0 = свободно, 1.0 = занято, 0.5 = неизвестно
        self.grid = np.full((height, width), 0.5, dtype=np.float32)
        
        # Логарифмические шансы для байесовского обновления
        self.log_odds = np.zeros((height, width), dtype=np.float32)
    
    def world_to_grid(self, point: Point) -> Tuple[int, int]:
        """
        Конвертирует мировые координаты в индексы сетки.
        
        Args:
            point: точка в мировых координатах
            
        Returns:
            (i, j) - индексы ячейки
        """
        i = int((point.y - self.origin.y) / self.resolution)
        j = int((point.x - self.origin.x) / self.resolution)
        return i, j
    
    def grid_to_world(self, i: int, j: int) -> Point:
        """
        Конвертирует индексы сетки в мировые координаты.
        
        Args:
            i, j: индексы ячейки
            
        Returns:
            Точка в мировых координатах (центр ячейки)
        """
        x = self.origin.x + (j + 0.5) * self.resolution
        y = self.origin.y + (i + 0.5) * self.resolution
        return Point(x, y)
    
    def is_in_bounds(self, i: int, j: int) -> bool:
        """
        Проверяет, находятся ли индексы в пределах сетки.
        
        Args:
            i, j: индексы ячейки
            
        Returns:
            True если индексы в пределах
        """
        return 0 <= i < self.height and 0 <= j < self.width
    
    def get_cell(self, i: int, j: int) -> float:
        """
        Возвращает вероятность занятости ячейки.
        
        Args:
            i, j: индексы ячейки
            
        Returns:
            Вероятность занятости [0.0, 1.0]
        """
        if not self.is_in_bounds(i, j):
            return 0.5  # Неизвестно для ячеек вне границ
        return float(self.grid[i, j])
    
    def set_cell(self, i: int, j: int, value: float) -> None:
        """
        Устанавливает вероятность занятости ячейки.
        
        Args:
            i, j: индексы ячейки
            value: вероятность занятости [0.0, 1.0]
        """
        if self.is_in_bounds(i, j):
            self.grid[i, j] = np.clip(value, 0.0, 1.0)
            # Обновляем log_odds
            if value == 0.5:
                self.log_odds[i, j] = 0.0
            else:
                self.log_odds[i, j] = np.log(value / (1.0 - value + 1e-10))
    
    def update_cell(self, i: int, j: int, log_odds_update: float) -> None:
        """
        Байесовское обновление ячейки через log-odds.
        
        Args:
            i, j: индексы ячейки
            log_odds_update: обновление log-odds
        """
        if not self.is_in_bounds(i, j):
            return
        
        # Обновляем log-odds
        self.log_odds[i, j] += log_odds_update
        
        # Ограничиваем значения
        LOG_ODDS_MIN = -5.0
        LOG_ODDS_MAX = 5.0
        self.log_odds[i, j] = np.clip(self.log_odds[i, j], LOG_ODDS_MIN, LOG_ODDS_MAX)
        
        # Конвертируем обратно в вероятность
        odds = np.exp(self.log_odds[i, j])
        self.grid[i, j] = odds / (1.0 + odds)
    
    def get_cells_along_ray(self, start: Point, end: Point) -> List[Tuple[int, int]]:
        """
        Возвращает все ячейки вдоль луча используя алгоритм Bresenham.
        
        Args:
            start: начальная точка луча
            end: конечная точка луча
            
        Returns:
            Список кортежей (i, j) ячеек вдоль луча
        """
        i0, j0 = self.world_to_grid(start)
        i1, j1 = self.world_to_grid(end)
        
        # Используем Bresenham для получения ячеек
        cells = bresenham_line(j0, i0, j1, i1)
        
        # Фильтруем ячейки, которые в пределах границ
        valid_cells = [(i, j) for j, i in cells if self.is_in_bounds(i, j)]
        
        return valid_cells
    
    def to_image(self) -> np.ndarray:
        """
        Конвертирует карту в изображение для визуализации.
        
        Returns:
            Grayscale numpy array (0-255)
            - 0 (черный) = занято
            - 255 (белый) = свободно
            - 128 (серый) = неизвестно
        """
        # Инвертируем: 0.0 (свободно) -> 255 (белый), 1.0 (занято) -> 0 (черный)
        image = (1.0 - self.grid) * 255.0
        return image.astype(np.uint8)
    
    def save(self, path: str) -> None:
        """
        Сохраняет карту в файл.
        
        Args:
            path: путь к файлу
        """
        data = {
            'width': self.width,
            'height': self.height,
            'resolution': self.resolution,
            'origin': (self.origin.x, self.origin.y),
            'grid': self.grid,
            'log_odds': self.log_odds
        }
        with open(path, 'wb') as f:
            pickle.dump(data, f)
    
    @classmethod
    def load(cls, path: str) -> 'OccupancyGrid':
        """
        Загружает карту из файла.
        
        Args:
            path: путь к файлу
            
        Returns:
            Экземпляр OccupancyGrid
        """
        with open(path, 'rb') as f:
            data = pickle.load(f)
        
        origin = Point(data['origin'][0], data['origin'][1])
        grid = cls(data['width'], data['height'], data['resolution'], origin)
        grid.grid = data['grid']
        grid.log_odds = data['log_odds']
        
        return grid

