"""
Алгоритм A* для поиска пути.
"""

import math
import heapq
from dataclasses import dataclass
from typing import List, Optional, Tuple
from src.common.types import Point
from src.mapping.occupancy_grid import OccupancyGrid


@dataclass
class Node:
    """Узел для алгоритма A*."""
    position: Tuple[int, int]
    g_cost: float  # Стоимость от старта
    h_cost: float  # Эвристика до цели
    f_cost: float  # g + h
    parent: Optional['Node'] = None
    
    def __lt__(self, other):
        """Для сравнения в приоритетной очереди."""
        return self.f_cost < other.f_cost


class AStar:
    """Алгоритм A* для поиска оптимального пути."""
    
    def __init__(self, grid: OccupancyGrid, robot_radius: float):
        """
        Args:
            grid: карта занятости
            robot_radius: радиус робота для буферизации препятствий
        """
        self.grid = grid
        self.robot_radius = robot_radius
        # Создаем "inflated" карту с буферизацией препятствий
        self.inflated_grid = self.inflate_obstacles(grid, robot_radius)
    
    def inflate_obstacles(self, grid: OccupancyGrid, radius: float) -> OccupancyGrid:
        """
        Создает карту с буферизацией препятствий на радиус робота.
        
        Args:
            grid: исходная карта
            radius: радиус буферизации
            
        Returns:
            Новая карта с буферизованными препятствиями
        """
        # Создаем копию карты
        inflated = OccupancyGrid(grid.width, grid.height, grid.resolution, grid.origin)
        inflated.grid = grid.grid.copy()
        inflated.log_odds = grid.log_odds.copy()
        
        # Количество ячеек для буферизации
        buffer_cells = int(math.ceil(radius / grid.resolution))
        
        # Применяем морфологическое расширение (dilation)
        new_grid = inflated.grid.copy()
        for i in range(grid.height):
            for j in range(grid.width):
                if grid.grid[i, j] > 0.7:  # Занятая ячейка
                    # Расширяем препятствие
                    for di in range(-buffer_cells, buffer_cells + 1):
                        for dj in range(-buffer_cells, buffer_cells + 1):
                            ni, nj = i + di, j + dj
                            if grid.is_in_bounds(ni, nj):
                                dist = math.sqrt(di*di + dj*dj) * grid.resolution
                                if dist <= radius:
                                    new_grid[ni, nj] = max(new_grid[ni, nj], 0.7)
        
        inflated.grid = new_grid
        return inflated
    
    def heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        """
        Эвристика (евклидово расстояние).
        
        Args:
            a, b: позиции (i, j)
            
        Returns:
            Евклидово расстояние
        """
        di = b[0] - a[0]
        dj = b[1] - a[1]
        return math.sqrt(di * di + dj * dj)
    
    def get_neighbors(self, node: Node) -> List[Node]:
        """
        Возвращает соседей узла (8-связность).
        
        Args:
            node: текущий узел
            
        Returns:
            Список соседних узлов
        """
        i, j = node.position
        neighbors = []
        
        # 8 направлений (включая диагонали)
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        
        for di, dj in directions:
            ni, nj = i + di, j + dj
            
            if self.is_valid_cell(ni, nj):
                # Стоимость перехода (диагональ дороже)
                if di != 0 and dj != 0:
                    move_cost = math.sqrt(2)  # Диагональ
                else:
                    move_cost = 1.0  # Горизонталь/вертикаль
                
                g_cost = node.g_cost + move_cost
                
                neighbor = Node(
                    position=(ni, nj),
                    g_cost=g_cost,
                    h_cost=0.0,  # Будет вычислено позже
                    f_cost=0.0,
                    parent=node
                )
                neighbors.append(neighbor)
        
        return neighbors
    
    def is_valid_cell(self, i: int, j: int) -> bool:
        """
        Проверяет, является ли ячейка валидной для прохода.
        
        Args:
            i, j: индексы ячейки
            
        Returns:
            True если ячейка свободна
        """
        if not self.inflated_grid.is_in_bounds(i, j):
            return False
        
        # Ячейка свободна если вероятность занятости < 0.5
        return self.inflated_grid.get_cell(i, j) < 0.5
    
    def find_path(self, start: Point, goal: Point) -> Optional[List[Point]]:
        """
        Находит путь от старта до цели используя A*.
        
        Args:
            start: начальная точка
            goal: целевая точка
            
        Returns:
            Список точек пути или None если путь не найден
        """
        # Конвертируем в координаты сетки
        start_i, start_j = self.inflated_grid.world_to_grid(start)
        goal_i, goal_j = self.inflated_grid.world_to_grid(goal)
        
        if not self.is_valid_cell(start_i, start_j):
            return None
        if not self.is_valid_cell(goal_i, goal_j):
            return None
        
        # Инициализация
        start_node = Node(
            position=(start_i, start_j),
            g_cost=0.0,
            h_cost=self.heuristic((start_i, start_j), (goal_i, goal_j)),
            f_cost=0.0
        )
        start_node.f_cost = start_node.g_cost + start_node.h_cost
        
        open_set = [start_node]
        closed_set = set()
        
        # Для отслеживания лучших путей
        g_scores = {(start_i, start_j): 0.0}
        
        while open_set:
            # Получаем узел с минимальным f_cost
            current = heapq.heappop(open_set)
            
            if current.position in closed_set:
                continue
            
            closed_set.add(current.position)
            
            # Проверяем, достигли ли цели
            if current.position == (goal_i, goal_j):
                # Восстанавливаем путь
                path = []
                node = current
                while node:
                    world_point = self.inflated_grid.grid_to_world(node.position[0], node.position[1])
                    path.append(world_point)
                    node = node.parent
                path.reverse()
                return path
            
            # Обрабатываем соседей
            for neighbor in self.get_neighbors(current):
                if neighbor.position in closed_set:
                    continue
                
                # Вычисляем h_cost
                neighbor.h_cost = self.heuristic(neighbor.position, (goal_i, goal_j))
                neighbor.f_cost = neighbor.g_cost + neighbor.h_cost
                
                # Проверяем, не нашли ли мы лучший путь к этому узлу
                if neighbor.position in g_scores:
                    if neighbor.g_cost >= g_scores[neighbor.position]:
                        continue
                
                g_scores[neighbor.position] = neighbor.g_cost
                heapq.heappush(open_set, neighbor)
        
        # Путь не найден
        return None

