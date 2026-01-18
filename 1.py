import pygame  
import numpy
import heapq 
import sys
import math
import random
#class Enviriment{}
#class Robot{}

# Определение цветов
# (R, G, B) format
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHT_GRAY = (200, 200, 200)
RED = (255, 0, 0) # Добавлен красный цвет для объекта

# Параметры окна
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 1000

# Параметры сетки
GRID_SIZE = 100 # Размер ячейки в пикселях

# Параметры объекта
OBJECT_SIZE = 50
# Начальные координаты объекта (верхний левый угол), привязанные к сетке
player_x = 50
player_y = 50
# Скорость перемещения (равна размеру ячейки)
object_speed = GRID_SIZE

def draw_grid(screen):
    """Функция для отрисовки сетки на экране."""
    for x in range(0, WINDOW_WIDTH, GRID_SIZE):
        pygame.draw.line(screen, LIGHT_GRAY, (x, 0), (x, WINDOW_HEIGHT), 1)
    for y in range(0, WINDOW_HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, LIGHT_GRAY, (0, y), (WINDOW_WIDTH, y), 1)

def draw_object(screen, x, y):
    """Функция для отрисовки перемещаемого объекта."""
    # Рисуем красный круг в текущих координатах
    pygame.draw.circle(screen, RED, (player_x, player_y,), 35)

def simulate_lidar_2d(position_x, position_y,  angle, obstacles, max_distance, fov, rays):
    """
    Симуляция 2D лидара.
    
    Args:
        position: (x, y) - позиция лидара
        angle: текущий угол поворота лидара (градусы)
        obstacles: список препятствий (прямоугольники, круги, линии)
        max_distance: максимальная дальность сканирования
        fov: поле зрения (градусы, обычно 360)
        rays: количество лучей
        
    Returns:
        Список расстояний для каждого луча
    """
    distances = []
    angle_step = fov / rays
    
    for i in range(rays):
        # Вычисляем угол текущего луча
        ray_angle = math.radians(angle + i * angle_step)
        
        # Начальная точка луча
        start_x = position_x
        start_y = position_y
        
        # Конечная точка луча (на максимальном расстоянии)
        end_x = start_x + max_distance * math.cos(ray_angle)
        end_y = start_y + max_distance * math.sin(ray_angle)
        
        # Ищем пересечения со всеми препятствиями
        min_distance = max_distance
        
        '''for obstacle in obstacles:
            # В зависимости от типа препятствия используем разную логику пересечения
            
            if isinstance(obstacle, pygame.Rect):
                # Пересечение луча с прямоугольником
                distance = ray_rect_intersection(
                    start_x, start_y, end_x, end_y, obstacle
                )
            elif isinstance(obstacle, tuple) and len(obstacle) == 3:
                # Круг: (x, y, radius)
                distance = ray_circle_intersection(
                    start_x, start_y, end_x, end_y, obstacle
                )
            
            if distance is not None and distance < min_distance:
                min_distance = distance
        '''
        distances.append(min_distance)
    
    return distances

def main():
    """Основная функция программы."""
    global player_x, player_y # Объявляем переменные глобальными, чтобы изменять их в функции main

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Pygame Grid with Moving Object")
    
    clock = pygame.time.Clock() # Добавляем часы для управления FPS

    running = True
    while running:
        

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Обработка нажатий клавиш
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    # Перемещаем влево, но не выходим за левую границу
                    player_x = max(50, player_x - object_speed)
                if event.key == pygame.K_RIGHT:
                    # Перемещаем вправо, но не выходим за правую границу
                    print(simulate_lidar_2d(player_x, player_y,  0, None, 300, 360, 360))
                    player_x = min(WINDOW_WIDTH - OBJECT_SIZE, player_x + object_speed)
                if event.key == pygame.K_UP:
                    # Перемещаем вверх, но не выходим за верхнюю границу
                    player_y = max(50, player_y - object_speed)
                if event.key == pygame.K_DOWN:
                    # Перемещаем вниз, но не выходим за нижнюю границу
                    player_y = min(WINDOW_HEIGHT - OBJECT_SIZE, player_y + object_speed)

        # Заливаем фон белым цветом
        screen.fill(WHITE)
        
        # Отрисовываем сетку
        draw_grid(screen)

        # Отрисовываем объект
        draw_object(screen, player_x, player_y)

        # Обновляем содержимое экрана
        pygame.display.flip()
        
        # Ограничиваем FPS для стабильности
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()


