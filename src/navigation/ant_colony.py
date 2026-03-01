"""
Алгоритм муравьиных колоний (ACO) для поиска пути.
"""

import math
import random
from typing import List, Optional, Tuple, Dict
from src.common.types import Point
from src.mapping.occupancy_grid import OccupancyGrid


class AntColony:
    """Алгоритм муравьиных колоний для поиска оптимального пути."""
    
    # 8 направлений (соседи)
    DIRECTIONS = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),           (0, 1),
        (1, -1),  (1, 0),  (1, 1)
    ]
    
    def __init__(self, grid: OccupancyGrid, robot_radius: float,
                 n_ants: int = 15, n_iterations: int = 40,
                 alpha: float = 1.0, beta: float = 2.0,
                 rho: float = 0.5, q: float = 100.0):
        """
        Args:
            grid: карта занятости
            robot_radius: радиус робота для буферизации
            n_ants: количество муравьёв
            n_iterations: количество итераций
            alpha: вес феромона
            beta: вес эвристики (привлекательность)
            rho: коэффициент испарения феромона
            q: количество феромона для отложения
        """
        self.grid = grid
        self.robot_radius = robot_radius
        self.n_ants = n_ants
        self.n_iterations = n_iterations
        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.q = q
        self.inflated_grid = self._inflate_obstacles(grid, robot_radius)
        # Феромоны на рёбрах: (i1,j1,i2,j2) -> значение (нормализуем ключ)
        self.pheromones: Dict[Tuple, float] = {}
        self._init_pheromones()
    
    def _inflate_obstacles(self, grid: OccupancyGrid, radius: float) -> OccupancyGrid:
        """Буферизация препятствий."""
        inflated = OccupancyGrid(grid.width, grid.height, grid.resolution, grid.origin)
        inflated.grid = grid.grid.copy()
        inflated.log_odds = grid.log_odds.copy()
        buffer_cells = int(math.ceil(radius / grid.resolution))
        new_grid = inflated.grid.copy()
        for i in range(grid.height):
            for j in range(grid.width):
                if grid.grid[i, j] > 0.7:
                    for di in range(-buffer_cells, buffer_cells + 1):
                        for dj in range(-buffer_cells, buffer_cells + 1):
                            ni, nj = i + di, j + dj
                            if grid.is_in_bounds(ni, nj):
                                dist = math.sqrt(di*di + dj*dj) * grid.resolution
                                if dist <= radius:
                                    new_grid[ni, nj] = max(new_grid[ni, nj], 0.7)
        inflated.grid = new_grid
        return inflated
    
    def _edge_key(self, a: Tuple[int, int], b: Tuple[int, int]) -> Tuple:
        """Нормализованный ключ для ребра (независимо от направления)."""
        return tuple(sorted([a, b]))
    
    def _init_pheromones(self) -> None:
        """Инициализация феромонов."""
        tau0 = 0.1
        for i in range(self.inflated_grid.height):
            for j in range(self.inflated_grid.width):
                if not self._is_valid(i, j):
                    continue
                for di, dj in self.DIRECTIONS:
                    ni, nj = i + di, j + dj
                    if self._is_valid(ni, nj):
                        key = self._edge_key((i, j), (ni, nj))
                        self.pheromones[key] = tau0
    
    def _is_valid(self, i: int, j: int) -> bool:
        """Ячейка свободна для прохода (включая неизвестные <= 0.5)."""
        if not self.inflated_grid.is_in_bounds(i, j):
            return False
        return self.inflated_grid.get_cell(i, j) <= 0.5
    
    def _heuristic(self, pos: Tuple[int, int], goal: Tuple[int, int]) -> float:
        """Эвристика: обратное расстояние до цели."""
        di = goal[0] - pos[0]
        dj = goal[1] - pos[1]
        dist = math.sqrt(di*di + dj*dj)
        return 1.0 / (dist + 0.01)
    
    def _get_pheromone(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        """Получить уровень феромона на ребре."""
        key = self._edge_key(a, b)
        return self.pheromones.get(key, 0.1)
    
    def _get_neighbors(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Свободные соседи."""
        i, j = pos
        neighbors = []
        for di, dj in self.DIRECTIONS:
            ni, nj = i + di, j + dj
            if self._is_valid(ni, nj):
                neighbors.append((ni, nj))
        return neighbors
    
    def _ant_walk(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """Один муравей ищет путь от start до goal."""
        path = [start]
        visited = {start}
        current = start
        
        max_steps = self.inflated_grid.width * self.inflated_grid.height
        for _ in range(max_steps):
            if current == goal:
                return path
            
            neighbors = [n for n in self._get_neighbors(current) if n not in visited]
            if not neighbors:
                return None
            
            # Вероятности перехода
            probs = []
            for n in neighbors:
                tau = self._get_pheromone(current, n)
                eta = self._heuristic(n, goal)
                p = (tau ** self.alpha) * (eta ** self.beta)
                probs.append((n, p))
            
            total = sum(p for _, p in probs)
            if total <= 0:
                return None
            
            # Выбор следующей ячейки (рулетка)
            r = random.random()
            for n, p in probs:
                r -= p / total
                if r <= 0:
                    path.append(n)
                    visited.add(n)
                    current = n
                    break
            else:
                n, _ = max(probs, key=lambda x: x[1])
                path.append(n)
                visited.add(n)
                current = n
        
        return None
    
    def _evaporate(self) -> None:
        """Испарение феромона."""
        for key in self.pheromones:
            self.pheromones[key] *= (1 - self.rho)
            self.pheromones[key] = max(0.01, self.pheromones[key])
    
    def _deposit_pheromone(self, path: List[Tuple[int, int]], amount: float) -> None:
        """Отложение феромона на пути."""
        for i in range(len(path) - 1):
            key = self._edge_key(path[i], path[i + 1])
            self.pheromones[key] = self.pheromones.get(key, 0.1) + amount
    
    def _path_length(self, path: List[Tuple[int, int]]) -> float:
        """Длина пути в единицах сетки."""
        length = 0.0
        for i in range(len(path) - 1):
            di = path[i+1][0] - path[i][0]
            dj = path[i+1][1] - path[i][1]
            length += math.sqrt(di*di + dj*dj)
        return length * self.inflated_grid.resolution
    
    def find_path(self, start: Point, goal: Point) -> Optional[List[Point]]:
        """
        Находит путь алгоритмом муравьиных колоний.

        Args:
            start: начальная точка
            goal: целевая точка

        Returns:
            Список точек пути или None
        """
        # Обновляем inflated_grid по текущей карте (карта могла измениться после mapping)
        self.inflated_grid = self._inflate_obstacles(self.grid, self.robot_radius)
        self._init_pheromones()
        start_ij = self.inflated_grid.world_to_grid(start)
        goal_ij = self.inflated_grid.world_to_grid(goal)
        
        if not self._is_valid(start_ij[0], start_ij[1]):
            return None
        if not self._is_valid(goal_ij[0], goal_ij[1]):
            return None
        
        best_path = None
        best_length = float('inf')
        
        for iteration in range(self.n_iterations):
            paths = []
            for _ in range(self.n_ants):
                path = self._ant_walk(start_ij, goal_ij)
                if path:
                    paths.append(path)
                    length = self._path_length(path)
                    if length < best_length:
                        best_length = length
                        best_path = path
            
            self._evaporate()
            
            for path in paths:
                length = self._path_length(path)
                if length > 0:
                    delta = self.q / length
                    self._deposit_pheromone(path, delta)
        
        if best_path is None:
            return None
        
        # Конвертируем в мировые координаты
        world_path = []
        for i, j in best_path:
            p = self.inflated_grid.grid_to_world(i, j)
            world_path.append(p)
        
        return world_path
    
    def is_valid_cell(self, i: int, j: int) -> bool:
        """Проверка ячейки для прохода."""
        return self._is_valid(i, j)
