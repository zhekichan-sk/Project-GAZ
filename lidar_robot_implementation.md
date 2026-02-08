# План имплементации: Симулятор лидарного картографирования робота

> **Спецификация**: [tech_spec.md](./tech_spec.md)  
> **Статус**: 🆕 Не начат  
> **Последнее обновление**: 2026-01-31

---

## 📋 Инструкция по использованию с DeepSeek

### Общие принципы работы с чат-ботом:

1. **Реализуй по одной фазе за раз**:
   - Скопируй в чат DeepSeek раздел нужной фазы целиком
   - Попроси: *"Реализуй код для Phase N согласно этому плану"*
   - При необходимости разбивай большие фазы на подзадачи (N.1, N.2, ...)
   
2. **Предоставляй контекст**:
   - В начале работы над проектом отправь DeepSeek структуру проекта
   - При реализации новой фазы — отправляй код зависимых модулей (из предыдущих фаз)
   - Копируй интерфейсы/базовые классы при реализации наследников

3. **Сохраняй код локально**:
   - DeepSeek не имеет доступа к файловой системе
   - Копируй сгенерированный код в файлы вручную
   - Проверяй работоспособность после каждой фазы

4. **Обнови статус после каждой фазы**:
   - Отметь выполненные задачи ✅ в этом документе
   - Запиши важные решения/отклонения от плана
   - Проверь, что код запускается без ошибок

5. **Итерируй при ошибках**:
   - Если код не работает — отправь ошибку DeepSeek с контекстом
   - Промпт: *"Вот ошибка: [ошибка]. Вот текущий код: [код]. Исправь."*

### Шаблон промпта для фазы:

```
Контекст проекта: Симулятор мобильного робота с лидарным датчиком для 
картографирования, локализации и навигации. Python 3.8+, Pygame, NumPy.

Текущая структура проекта:
[вставь дерево файлов]

Зависимые модули (код):
[вставь код модулей, от которых зависит текущая фаза]

Задача: Реализуй Phase N — [название фазы]
[вставь содержимое фазы из этого документа]

Требования:
- Полный рабочий код (не заглушки)
- Type hints для всех функций
- Docstrings для публичных методов
- Обработка ошибок
```

---

## 🎯 Обзор проекта

### Назначение
Интерактивный симулятор мобильного робота с функциями:
- Симуляция 2D-среды с препятствиями
- Виртуальный лидар (лазерный дальномер)
- Построение карты (Occupancy Grid)
- Локализация на известной карте
- Планирование оптимального маршрута (A*)
- Графический интерфейс

### Технологический стек
- **Язык**: Python 3.8+
- **GUI**: Pygame
- **Вычисления**: NumPy, SciPy
- **Визуализация**: matplotlib (опционально)

### Структура проекта

```
lidar_robot_simulator/
├── README.md
├── requirements.txt
├── configs/
│   ├── default_environment.json
│   └── robot_config.json
├── src/
│   ├── __init__.py
│   ├── common/
│   │   ├── __init__.py
│   │   ├── types.py          # Enum'ы, константы
│   │   ├── geometry.py       # Геометрические утилиты
│   │   └── config_loader.py  # Загрузка конфигов
│   ├── simulation/
│   │   ├── __init__.py
│   │   ├── environment.py    # Среда с препятствиями
│   │   ├── robot.py          # Модель робота
│   │   └── lidar.py          # Виртуальный лидар
│   ├── mapping/
│   │   ├── __init__.py
│   │   ├── occupancy_grid.py # Карта занятости
│   │   └── mapper.py         # Построитель карты
│   ├── localization/
│   │   ├── __init__.py
│   │   ├── scan_matcher.py   # Сопоставление сканов
│   │   └── localizer.py      # Модуль локализации
│   ├── navigation/
│   │   ├── __init__.py
│   │   ├── astar.py          # Алгоритм A*
│   │   └── path_planner.py   # Планировщик пути
│   └── gui/
│       ├── __init__.py
│       ├── main_window.py    # Главное окно
│       ├── renderer.py       # Отрисовка элементов
│       ├── controls.py       # Панель управления
│       └── visualizer.py     # Визуализация карты/пути
├── tests/
│   ├── __init__.py
│   ├── test_geometry.py
│   ├── test_lidar.py
│   ├── test_mapping.py
│   ├── test_localization.py
│   └── test_pathfinding.py
└── main.py                   # Точка входа
```

---

## Phase 0: Подготовка инфраструктуры

> **Цель**: Создать базовую структуру проекта и общие утилиты  
> **Зависимости**: Нет  
> **Статус**: ⬜ Не начат

### 0.1 Инициализация проекта

- [ ] Создать структуру директорий (как показано выше)
- [ ] `requirements.txt`:
  ```
  pygame>=2.5.0
  numpy>=1.24.0
  scipy>=1.10.0
  matplotlib>=3.7.0
  ```
- [ ] `README.md` — описание проекта, инструкция по запуску

### 0.2 Общие типы и константы

- [ ] `src/common/__init__.py` — публичный API модуля
- [ ] `src/common/types.py`:
  - [ ] `Point` — namedtuple или dataclass для координат (x, y)
  - [ ] `Pose` — позиция + ориентация (x, y, theta)
  - [ ] `RobotState` — enum (IDLE, MOVING, MAPPING, LOCALIZING, NAVIGATING)
  - [ ] `SimulationMode` — enum (MAPPING, LOCALIZATION, NAVIGATION)
  - [ ] `ObstacleType` — enum (WALL, RECTANGLE, POLYGON, CIRCLE)
  - [ ] Константы: DEFAULT_FPS, DEFAULT_ROBOT_RADIUS, DEFAULT_LIDAR_RANGE

### 0.3 Геометрические утилиты

- [ ] `src/common/geometry.py`:
  - [ ] `distance(p1: Point, p2: Point) -> float` — расстояние между точками
  - [ ] `angle_between(p1: Point, p2: Point) -> float` — угол в радианах
  - [ ] `normalize_angle(angle: float) -> float` — нормализация в [-π, π]
  - [ ] `rotate_point(point: Point, origin: Point, angle: float) -> Point`
  - [ ] `line_intersection(line1, line2) -> Point | None` — пересечение отрезков
  - [ ] `point_in_polygon(point: Point, polygon: list[Point]) -> bool`
  - [ ] `ray_segment_intersection(ray_origin, ray_angle, segment) -> Point | None`

### 0.4 Загрузчик конфигурации

- [ ] `src/common/config_loader.py`:
  - [ ] `load_environment_config(path: str) -> dict` — загрузка JSON среды
  - [ ] `load_robot_config(path: str) -> dict` — загрузка настроек робота
  - [ ] `validate_config(config: dict, schema: str) -> bool` — валидация
  - [ ] Обработка ошибок при отсутствии/повреждении файла

### 0.5 Конфигурационные файлы

- [ ] `configs/default_environment.json`:
  ```json
  {
    "environment": {
      "name": "Default Room",
      "width": 800,
      "height": 600,
      "background_color": [40, 40, 40]
    },
    "obstacles": [
      {"type": "wall", "x1": 50, "y1": 50, "x2": 750, "y2": 50},
      {"type": "wall", "x1": 50, "y1": 550, "x2": 750, "y2": 550},
      {"type": "wall", "x1": 50, "y1": 50, "x2": 50, "y2": 550},
      {"type": "wall", "x1": 750, "y1": 50, "x2": 750, "y2": 550},
      {"type": "rectangle", "x": 300, "y": 200, "width": 100, "height": 150}
    ]
  }
  ```

- [ ] `configs/robot_config.json`:
  ```json
  {
    "robot": {
      "radius": 15,
      "color": [0, 150, 255],
      "speed": 100,
      "rotation_speed": 2.0,
      "start_position": [400, 300],
      "start_angle": 0
    },
    "lidar": {
      "num_rays": 360,
      "max_range": 300,
      "fov": 360,
      "noise_std": 1.0,
      "angle_resolution": 1.0
    }
  }
  ```

### DoD Phase 0:
- [ ] `python -c "from src.common import Point, Pose, distance"` работает
- [ ] Конфиги загружаются без ошибок
- [ ] Геометрические функции работают корректно (проверить вручную)
- [ ] Структура проекта соответствует плану

---

## Phase 1: Симуляция среды

> **Цель**: Создать модуль 2D-среды с препятствиями  
> **Зависимости**: Phase 0  
> **Статус**: ⬜ Не начат

### 1.1 Базовые классы препятствий

- [ ] `src/simulation/__init__.py` — публичный API
- [ ] `src/simulation/obstacles.py`:
  - [ ] `Obstacle` — абстрактный базовый класс:
    - [ ] `contains_point(point: Point) -> bool`
    - [ ] `intersects_ray(origin: Point, angle: float, max_dist: float) -> float | None`
    - [ ] `get_bounding_box() -> tuple[Point, Point]`
    - [ ] `draw(surface: pygame.Surface) -> None`
  - [ ] `Wall(Obstacle)` — линейная стена (x1, y1, x2, y2)
  - [ ] `Rectangle(Obstacle)` — прямоугольник (x, y, width, height)
  - [ ] `Polygon(Obstacle)` — произвольный многоугольник (points: list[Point])
  - [ ] `Circle(Obstacle)` — круглое препятствие (center, radius)

### 1.2 Класс среды

- [ ] `src/simulation/environment.py`:
  - [ ] `Environment`:
    - [ ] `__init__(width: int, height: int, obstacles: list[Obstacle])`
    - [ ] `width`, `height` — размеры области
    - [ ] `obstacles` — список препятствий
    - [ ] `background_color` — цвет фона
    - [ ] `add_obstacle(obstacle: Obstacle) -> None`
    - [ ] `remove_obstacle(obstacle: Obstacle) -> None`
    - [ ] `is_valid_position(point: Point, radius: float) -> bool` — проверка на коллизию
    - [ ] `raycast(origin: Point, angle: float, max_dist: float) -> float` — трассировка луча
    - [ ] `draw(surface: pygame.Surface) -> None` — отрисовка среды
    - [ ] `@classmethod from_config(config: dict) -> Environment` — создание из JSON
    - [ ] `to_config() -> dict` — сериализация в JSON

### 1.3 Фабрика препятствий

- [ ] `src/simulation/obstacle_factory.py`:
  - [ ] `create_obstacle(config: dict) -> Obstacle` — создание из конфига
  - [ ] Поддержка всех типов: wall, rectangle, polygon, circle

### DoD Phase 1:
- [ ] Среда создаётся из JSON-конфига
- [ ] `environment.raycast()` корректно находит пересечения со всеми типами препятствий
- [ ] `environment.is_valid_position()` учитывает радиус объекта
- [ ] `environment.draw()` отображает все препятствия

### Промпт для DeepSeek:
```
Реализуй Phase 1 — модуль симуляции среды с препятствиями.

Используй базовые типы из Phase 0:
[вставь код src/common/types.py и src/common/geometry.py]

Требования:
1. Абстрактный класс Obstacle с методами intersects_ray, contains_point, draw
2. Конкретные классы: Wall, Rectangle, Polygon, Circle
3. Класс Environment, который загружается из JSON и поддерживает raycast
4. Pygame для отрисовки

Формат JSON среды:
[вставь пример configs/default_environment.json]
```

---

## Phase 2: Модель робота

> **Цель**: Реализовать модель робота с управлением  
> **Зависимости**: Phase 1  
> **Статус**: ⬜ Не начат

### 2.1 Класс робота

- [ ] `src/simulation/robot.py`:
  - [ ] `Robot`:
    - [ ] `__init__(x, y, theta, radius, speed, rotation_speed)`
    - [ ] `pose: Pose` — текущая позиция и ориентация
    - [ ] `radius: float` — радиус робота
    - [ ] `speed: float` — линейная скорость (ед/сек)
    - [ ] `rotation_speed: float` — угловая скорость (рад/сек)
    - [ ] `color: tuple` — цвет для отрисовки
    - [ ] `trajectory: list[Point]` — история перемещений (для визуализации)
    - [ ] `state: RobotState` — текущее состояние
    - [ ] `move_forward(dt: float, environment: Environment) -> bool` — движение вперёд с проверкой коллизий
    - [ ] `move_backward(dt: float, environment: Environment) -> bool`
    - [ ] `rotate_left(dt: float) -> None`
    - [ ] `rotate_right(dt: float) -> None`
    - [ ] `set_position(x, y, theta) -> None` — телепортация
    - [ ] `get_odometry() -> Pose` — текущая одометрия (с накопленной ошибкой)
    - [ ] `add_odometry_noise(noise_linear: float, noise_angular: float)` — симуляция неточности
    - [ ] `draw(surface: pygame.Surface) -> None` — отрисовка (круг + направление)
    - [ ] `draw_trajectory(surface: pygame.Surface) -> None`
    - [ ] `clear_trajectory() -> None`
    - [ ] `@classmethod from_config(config: dict) -> Robot`

### 2.2 Контроллер управления

- [ ] `src/simulation/robot_controller.py`:
  - [ ] `RobotController`:
    - [ ] `__init__(robot: Robot, environment: Environment)`
    - [ ] `handle_input(keys: pygame.key.ScancodeWrapper, dt: float) -> None`
    - [ ] Управление: W/↑ — вперёд, S/↓ — назад, A/← — влево, D/→ — вправо
    - [ ] `is_collision() -> bool`
    - [ ] `get_movement_delta() -> tuple[float, float, float]` — (dx, dy, dtheta)

### DoD Phase 2:
- [ ] Робот создаётся из конфига
- [ ] Управление с клавиатуры работает плавно
- [ ] Коллизии с препятствиями предотвращают проход сквозь стены
- [ ] Траектория визуализируется
- [ ] Одометрия возвращает позицию (опционально: с шумом)

### Промпт для DeepSeek:
```
Реализуй Phase 2 — модель робота с ручным управлением.

Контекст:
[вставь код Environment и Obstacle из Phase 1]
[вставь код types.py с Point, Pose, RobotState]

Требования:
1. Класс Robot с позицией, скоростью, управлением движением
2. Проверка коллизий через Environment.is_valid_position()
3. Сохранение траектории для визуализации
4. Управление WASD/стрелками через RobotController
5. Отрисовка: круг + линия направления
```

---

## Phase 3: Виртуальный лидар

> **Цель**: Реализовать симуляцию лазерного дальномера  
> **Зависимости**: Phase 1, Phase 2  
> **Статус**: ⬜ Не начат

### 3.1 Класс лидара

- [ ] `src/simulation/lidar.py`:
  - [ ] `LidarScan` — dataclass для результата скана:
    - [ ] `angles: np.ndarray` — углы лучей
    - [ ] `distances: np.ndarray` — измеренные расстояния
    - [ ] `points: list[Point]` — точки в глобальных координатах
    - [ ] `timestamp: float`
    - [ ] `robot_pose: Pose` — позиция робота при сканировании
  
  - [ ] `Lidar`:
    - [ ] `__init__(num_rays, max_range, fov, noise_std, angle_resolution)`
    - [ ] `num_rays: int` — количество лучей (360)
    - [ ] `max_range: float` — максимальная дальность
    - [ ] `fov: float` — угол обзора в градусах (360 = полный круг)
    - [ ] `noise_std: float` — стандартное отклонение шума
    - [ ] `angle_resolution: float` — разрешение по углу
    - [ ] `scan(robot: Robot, environment: Environment) -> LidarScan`:
      - [ ] Для каждого луча вызвать `environment.raycast()`
      - [ ] Добавить гауссовский шум к измерениям
      - [ ] Конвертировать в глобальные координаты
    - [ ] `get_ray_angles() -> np.ndarray` — массив углов лучей
    - [ ] `draw_rays(surface, robot, scan, color) -> None` — визуализация лучей
    - [ ] `draw_points(surface, scan, color, radius) -> None` — визуализация точек
    - [ ] `@classmethod from_config(config: dict) -> Lidar`

### 3.2 Визуализация лидара

- [ ] Два режима отображения:
  - [ ] Линии (лучи) от робота до точек
  - [ ] Точки на препятствиях

### DoD Phase 3:
- [ ] Лидар корректно измеряет расстояния до всех типов препятствий
- [ ] Шум добавляется к измерениям
- [ ] `max_range` ограничивает измерения
- [ ] Визуализация лучей/точек работает
- [ ] Скан включает глобальные координаты точек

### Промпт для DeepSeek:
```
Реализуй Phase 3 — виртуальный лидар (лазерный дальномер).

Контекст:
[вставь код Environment.raycast() из Phase 1]
[вставь код Robot с Pose из Phase 2]

Требования:
1. Класс Lidar с настраиваемыми параметрами (num_rays, max_range, fov, noise)
2. Метод scan() возвращает LidarScan с:
   - Массивом углов
   - Массивом расстояний
   - Списком точек в глобальных координатах
3. Добавление гауссовского шума (numpy.random.normal)
4. Визуализация лучей и/или точек через pygame
```

---

## Phase 4: Построение карты (Occupancy Grid)

> **Цель**: Реализовать алгоритм построения карты занятости  
> **Зависимости**: Phase 3  
> **Статус**: ⬜ Не начат

### 4.1 Карта занятости

- [ ] `src/mapping/__init__.py` — публичный API
- [ ] `src/mapping/occupancy_grid.py`:
  - [ ] `OccupancyGrid`:
    - [ ] `__init__(width, height, resolution, origin)`:
      - [ ] `width`, `height` — размеры в ячейках
      - [ ] `resolution` — размер ячейки в единицах (например, 5 = 5x5)
      - [ ] `origin: Point` — координаты левого нижнего угла
    - [ ] `grid: np.ndarray` — 2D массив вероятностей [0.0, 1.0]
      - [ ] 0.0 = свободно, 1.0 = занято, 0.5 = неизвестно
    - [ ] `log_odds: np.ndarray` — логарифмические шансы (для байесовского обновления)
    - [ ] `world_to_grid(point: Point) -> tuple[int, int]` — мировые → индексы
    - [ ] `grid_to_world(i: int, j: int) -> Point` — индексы → мировые
    - [ ] `is_in_bounds(i: int, j: int) -> bool`
    - [ ] `get_cell(i: int, j: int) -> float` — вероятность занятости
    - [ ] `set_cell(i: int, j: int, value: float) -> None`
    - [ ] `update_cell(i: int, j: int, log_odds_update: float) -> None` — байесовское обновление
    - [ ] `get_cells_along_ray(start: Point, end: Point) -> list[tuple[int, int]]` — Bresenham
    - [ ] `to_image() -> np.ndarray` — для визуализации (grayscale)
    - [ ] `save(path: str) -> None` — сохранение в файл
    - [ ] `@classmethod load(path: str) -> OccupancyGrid`

### 4.2 Построитель карты

- [ ] `src/mapping/mapper.py`:
  - [ ] Константы:
    - [ ] `LOG_ODDS_FREE = -0.4` — свободная ячейка
    - [ ] `LOG_ODDS_OCCUPIED = 0.85` — занятая ячейка
    - [ ] `LOG_ODDS_PRIOR = 0.0` — начальное значение
    - [ ] `LOG_ODDS_MIN = -5.0`, `LOG_ODDS_MAX = 5.0` — ограничения
  
  - [ ] `Mapper`:
    - [ ] `__init__(grid: OccupancyGrid)`
    - [ ] `update_from_scan(scan: LidarScan) -> None`:
      - [ ] Для каждого луча:
        - [ ] Получить ячейки вдоль луча (Bresenham)
        - [ ] Обновить свободные ячейки (LOG_ODDS_FREE)
        - [ ] Обновить конечную ячейку (LOG_ODDS_OCCUPIED)
    - [ ] `get_completion_percentage() -> float` — % исследованной карты
    - [ ] `reset() -> None` — сброс карты

### 4.3 Алгоритм Bresenham

- [ ] `src/mapping/bresenham.py`:
  - [ ] `bresenham_line(x0, y0, x1, y1) -> list[tuple[int, int]]`
  - [ ] Возвращает все ячейки между двумя точками

### DoD Phase 4:
- [ ] Карта создаётся с заданным разрешением
- [ ] `world_to_grid` / `grid_to_world` конвертируют координаты корректно
- [ ] Bresenham возвращает все ячейки вдоль луча
- [ ] `Mapper.update_from_scan()` обновляет карту на основе скана
- [ ] Карта визуализируется (чёрный=занято, белый=свободно, серый=неизвестно)
- [ ] Карту можно сохранить/загрузить

### Промпт для DeepSeek:
```
Реализуй Phase 4 — построение карты методом Occupancy Grid.

Контекст:
[вставь код LidarScan из Phase 3]

Требования:
1. OccupancyGrid — 2D массив вероятностей занятости
2. Байесовское обновление через log-odds
3. Конвертация мировых координат ↔ индексы ячеек
4. Алгоритм Bresenham для получения ячеек вдоль луча
5. Mapper.update_from_scan() обновляет карту по данным лидара:
   - Ячейки вдоль луча → свободные
   - Конечная точка луча → занятая
6. Метод to_image() для визуализации (grayscale numpy array)
```

---

## Phase 5: Локализация

> **Цель**: Реализовать определение позиции робота на известной карте  
> **Зависимости**: Phase 3, Phase 4  
> **Статус**: ⬜ Не начат

### 5.1 Сопоставление сканов (Scan Matching)

- [ ] `src/localization/__init__.py` — публичный API
- [ ] `src/localization/scan_matcher.py`:
  - [ ] `ScanMatcher`:
    - [ ] `__init__(grid: OccupancyGrid)`
    - [ ] `compute_score(scan: LidarScan, pose: Pose) -> float`:
      - [ ] Для каждой точки скана вычислить позицию на карте
      - [ ] Суммировать вероятности занятости в этих ячейках
      - [ ] Высокий score = хорошее совпадение
    - [ ] `search_best_pose(scan: LidarScan, initial_pose: Pose, search_radius: float, angular_range: float) -> tuple[Pose, float]`:
      - [ ] Поиск лучшей позиции в окрестности initial_pose
      - [ ] Возвращает (best_pose, confidence)

### 5.2 Модуль локализации

- [ ] `src/localization/localizer.py`:
  - [ ] `LocalizationResult` — dataclass:
    - [ ] `pose: Pose` — оценённая позиция
    - [ ] `confidence: float` — уверенность [0.0, 1.0]
    - [ ] `error: float` — отклонение от реальной позиции (если известна)
  
  - [ ] `Localizer`:
    - [ ] `__init__(grid: OccupancyGrid, scan_matcher: ScanMatcher)`
    - [ ] `localize(scan: LidarScan, odometry_pose: Pose) -> LocalizationResult`:
      - [ ] Использовать одометрию как начальную оценку
      - [ ] Уточнить позицию через scan matching
    - [ ] `global_localization(scan: LidarScan) -> LocalizationResult`:
      - [ ] Поиск позиции без начальной оценки (медленнее)
    - [ ] `get_position_error(estimated: Pose, actual: Pose) -> float`

### 5.3 Оценка неопределённости

- [ ] Визуализация "облака" возможных позиций (опционально, упрощённо)

### DoD Phase 5:
- [ ] `ScanMatcher.compute_score()` корректно оценивает совпадение
- [ ] `Localizer.localize()` возвращает позицию с ошибкой ≤ 5% от размера карты
- [ ] Confidence отражает уверенность в оценке
- [ ] Работает в реальном времени (≤ 50 мс на локализацию)

### Промпт для DeepSeek:
```
Реализуй Phase 5 — локализация робота на известной карте.

Контекст:
[вставь код OccupancyGrid из Phase 4]
[вставь код LidarScan из Phase 3]

Требования:
1. ScanMatcher — сопоставление скана с картой:
   - compute_score() — оценка совпадения скана с картой для данной позы
   - search_best_pose() — поиск лучшей позиции в окрестности
2. Localizer — модуль локализации:
   - localize() — уточнение позиции на основе одометрии + scan matching
   - Возвращает LocalizationResult с pose и confidence
3. Точность ≤ 5% от размера карты
4. Время работы ≤ 50 мс
```

---

## Phase 6: Планирование пути (A*)

> **Цель**: Реализовать поиск оптимального маршрута  
> **Зависимости**: Phase 4  
> **Статус**: ⬜ Не начат

### 6.1 Алгоритм A*

- [ ] `src/navigation/__init__.py` — публичный API
- [ ] `src/navigation/astar.py`:
  - [ ] `Node` — dataclass для узла поиска:
    - [ ] `position: tuple[int, int]`
    - [ ] `g_cost: float` — стоимость от старта
    - [ ] `h_cost: float` — эвристика до цели
    - [ ] `f_cost: float` — g + h
    - [ ] `parent: Node | None`
  
  - [ ] `AStar`:
    - [ ] `__init__(grid: OccupancyGrid, robot_radius: float)`:
      - [ ] Создать "inflated" карту (буферизация препятствий на robot_radius)
    - [ ] `heuristic(a: tuple, b: tuple) -> float` — евклидово расстояние
    - [ ] `get_neighbors(node: Node) -> list[Node]` — 8 соседей (с диагоналями)
    - [ ] `is_valid_cell(i: int, j: int) -> bool` — проверка на занятость
    - [ ] `find_path(start: Point, goal: Point) -> list[Point] | None`:
      - [ ] Конвертировать в координаты сетки
      - [ ] Выполнить A* поиск
      - [ ] Конвертировать результат в мировые координаты
      - [ ] Вернуть None если путь не найден
    - [ ] `inflate_obstacles(grid: OccupancyGrid, radius: float) -> OccupancyGrid`

### 6.2 Планировщик пути

- [ ] `src/navigation/path_planner.py`:
  - [ ] `PathPlanningResult` — dataclass:
    - [ ] `path: list[Point]` — список точек пути
    - [ ] `length: float` — длина пути
    - [ ] `found: bool` — найден ли путь
  
  - [ ] `PathPlanner`:
    - [ ] `__init__(grid: OccupancyGrid, robot_radius: float)`
    - [ ] `astar: AStar` — экземпляр алгоритма
    - [ ] `plan(start: Point, goal: Point) -> PathPlanningResult`
    - [ ] `smooth_path(path: list[Point]) -> list[Point]` — сглаживание (опционально)
    - [ ] `is_goal_reachable(goal: Point) -> bool` — проверка доступности цели
    - [ ] `get_path_length(path: list[Point]) -> float`

### DoD Phase 6:
- [ ] A* находит путь между двумя точками
- [ ] Путь обходит препятствия с учётом радиуса робота
- [ ] Время поиска ≤ 100 мс для карты 200×150 ячеек
- [ ] Возвращает None если путь невозможен
- [ ] Путь оптимален (или близок к оптимальному)

### Промпт для DeepSeek:
```
Реализуй Phase 6 — планирование пути алгоритмом A*.

Контекст:
[вставь код OccupancyGrid из Phase 4]

Требования:
1. Алгоритм A* с евклидовой эвристикой
2. 8-связность (диагональные переходы)
3. Буферизация препятствий на радиус робота (inflate)
4. AStar.find_path(start, goal) → list[Point] или None
5. PathPlanner как обёртка с дополнительными методами
6. Время поиска ≤ 100 мс
7. Используй heapq для приоритетной очереди
```

---

## Phase 7: Графический интерфейс

> **Цель**: Создать интерактивный GUI с режимами работы  
> **Зависимости**: Phase 1-6  
> **Статус**: ⬜ Не начат

### 7.1 Главное окно

- [ ] `src/gui/__init__.py` — публичный API
- [ ] `src/gui/main_window.py`:
  - [ ] `MainWindow`:
    - [ ] `__init__(width, height, title)`
    - [ ] `screen: pygame.Surface`
    - [ ] `clock: pygame.Clock`
    - [ ] `fps: int`
    - [ ] `running: bool`
    - [ ] `current_mode: SimulationMode`
    - [ ] `run() -> None` — главный цикл
    - [ ] `handle_events() -> None` — обработка событий
    - [ ] `update(dt: float) -> None` — обновление логики
    - [ ] `render() -> None` — отрисовка
    - [ ] `switch_mode(mode: SimulationMode) -> None`
    - [ ] `on_mouse_click(pos: tuple, button: int) -> None`

### 7.2 Рендерер

- [ ] `src/gui/renderer.py`:
  - [ ] `Renderer`:
    - [ ] `__init__(screen: pygame.Surface)`
    - [ ] `render_environment(env: Environment) -> None`
    - [ ] `render_robot(robot: Robot) -> None`
    - [ ] `render_lidar_scan(scan: LidarScan, mode: str) -> None` — "rays" или "points"
    - [ ] `render_occupancy_grid(grid: OccupancyGrid, alpha: int) -> None`
    - [ ] `render_path(path: list[Point], color: tuple) -> None`
    - [ ] `render_goal(goal: Point) -> None`
    - [ ] `render_trajectory(trajectory: list[Point]) -> None`

### 7.3 Панель управления (HUD)

- [ ] `src/gui/hud.py`:
  - [ ] `HUD`:
    - [ ] `__init__(screen, font_size)`
    - [ ] `render(robot: Robot, mode: SimulationMode, info: dict) -> None`
    - [ ] Отображение:
      - [ ] Текущий режим
      - [ ] Позиция робота (x, y, θ)
      - [ ] FPS
      - [ ] Прогресс картографирования (%)
      - [ ] Статус локализации (confidence)
      - [ ] Длина пути (если есть)
    - [ ] Подсказки по управлению (внизу экрана)

### 7.4 Интеграция режимов

- [ ] `src/gui/modes/`:
  - [ ] `base_mode.py` — абстрактный базовый режим
  - [ ] `mapping_mode.py`:
    - [ ] Ручное управление роботом
    - [ ] Визуализация лидара
    - [ ] Построение карты в реальном времени
    - [ ] Клавиша M — сохранить карту
  - [ ] `localization_mode.py`:
    - [ ] Загрузка сохранённой карты
    - [ ] Визуализация карты
    - [ ] Локализация робота
    - [ ] Отображение estimated vs actual позиции
  - [ ] `navigation_mode.py`:
    - [ ] Загрузка карты
    - [ ] Клик мышью — установка цели
    - [ ] Планирование и отображение пути
    - [ ] Автоматическое движение по пути (опционально)

### 7.5 Управление

- [ ] Клавиатура:
  - [ ] W/↑, S/↓, A/←, D/→ — управление роботом
  - [ ] 1, 2, 3 — переключение режимов
  - [ ] R — сброс позиции робота
  - [ ] C — очистка карты/траектории
  - [ ] M — сохранить карту
  - [ ] L — загрузить карту
  - [ ] ESC — выход
- [ ] Мышь:
  - [ ] ЛКМ — установка цели (режим навигации)
  - [ ] ПКМ — телепортация робота (отладка)

### DoD Phase 7:
- [ ] Приложение запускается и отображает среду + робота
- [ ] Управление с клавиатуры работает плавно (30+ FPS)
- [ ] Три режима переключаются клавишами 1/2/3
- [ ] HUD отображает всю необходимую информацию
- [ ] В режиме навигации клик устанавливает цель и показывает путь

### Промпт для DeepSeek:
```
Реализуй Phase 7 — графический интерфейс на Pygame.

Контекст:
[вставь интерфейсы всех модулей из Phase 1-6]

Требования:
1. Главный цикл с обработкой событий, обновлением, отрисовкой
2. Три режима: MAPPING, LOCALIZATION, NAVIGATION
3. Рендерер для всех элементов (среда, робот, лидар, карта, путь)
4. HUD с информацией о состоянии
5. Управление: WASD, 1/2/3 режимы, клик для цели
6. 30+ FPS
```

---

## Phase 8: Интеграция и главный модуль

> **Цель**: Собрать все компоненты в единое приложение  
> **Зависимости**: Phase 7  
> **Статус**: ⬜ Не начат

### 8.1 Главный модуль

- [ ] `main.py`:
  - [ ] Парсинг аргументов командной строки (argparse):
    - [ ] `--config` — путь к конфигу среды
    - [ ] `--width`, `--height` — размер окна
    - [ ] `--mode` — начальный режим (mapping/localization/navigation)
    - [ ] `--map` — путь к загружаемой карте
  - [ ] Инициализация всех модулей
  - [ ] Запуск главного окна
  - [ ] Корректное завершение (cleanup)

### 8.2 Класс приложения

- [ ] `src/app.py`:
  - [ ] `Application`:
    - [ ] `__init__(config_path: str)`
    - [ ] `environment: Environment`
    - [ ] `robot: Robot`
    - [ ] `lidar: Lidar`
    - [ ] `occupancy_grid: OccupancyGrid`
    - [ ] `mapper: Mapper`
    - [ ] `localizer: Localizer`
    - [ ] `path_planner: PathPlanner`
    - [ ] `main_window: MainWindow`
    - [ ] `setup() -> None` — инициализация
    - [ ] `run() -> None` — запуск
    - [ ] `cleanup() -> None` — очистка ресурсов

### 8.3 Демонстрационные конфиги

- [ ] `configs/demo_office.json` — офисное помещение
- [ ] `configs/demo_maze.json` — лабиринт
- [ ] `configs/demo_open.json` — открытое пространство с объектами

### DoD Phase 8:
- [ ] `python main.py` запускает приложение с дефолтным конфигом
- [ ] `python main.py --config configs/demo_maze.json` работает
- [ ] Все три режима работают корректно
- [ ] Приложение корректно завершается по ESC

---

## Phase 9: Тестирование и документация

> **Цель**: Покрыть код тестами и документацией  
> **Зависимости**: Phase 8  
> **Статус**: ⬜ Не начат

### 9.1 Unit-тесты

- [ ] `tests/test_geometry.py`:
  - [ ] Тесты distance, angle_between, normalize_angle
  - [ ] Тесты ray_segment_intersection
  - [ ] Тесты point_in_polygon

- [ ] `tests/test_lidar.py`:
  - [ ] Тест сканирования пустой среды (все max_range)
  - [ ] Тест сканирования с препятствиями
  - [ ] Тест добавления шума

- [ ] `tests/test_mapping.py`:
  - [ ] Тест world_to_grid / grid_to_world
  - [ ] Тест Bresenham
  - [ ] Тест обновления карты из скана

- [ ] `tests/test_localization.py`:
  - [ ] Тест compute_score с идеальным совпадением
  - [ ] Тест локализации с известной картой

- [ ] `tests/test_pathfinding.py`:
  - [ ] Тест A* на пустой карте (прямая линия)
  - [ ] Тест A* с препятствиями
  - [ ] Тест недостижимой цели

### 9.2 Интеграционные тесты

- [ ] `tests/test_integration.py`:
  - [ ] Полный цикл: создание среды → сканирование → построение карты
  - [ ] Цикл: карта → локализация → проверка точности
  - [ ] Цикл: карта → планирование → валидация пути

### 9.3 Документация

- [ ] `README.md`:
  - [ ] Описание проекта
  - [ ] Установка зависимостей
  - [ ] Запуск приложения
  - [ ] Описание режимов
  - [ ] Управление
  - [ ] Скриншоты/GIF

- [ ] Docstrings для всех публичных классов и методов

### DoD Phase 9:
- [ ] `pytest tests/` проходит без ошибок
- [ ] README содержит инструкции по установке и использованию
- [ ] Все публичные методы имеют docstrings

---

## 📊 Сводка прогресса

| Phase | Описание | Статус | Файлов |
|-------|----------|--------|--------|
| 0 | Подготовка инфраструктуры | ⬜ | 6 |
| 1 | Симуляция среды | ⬜ | 4 |
| 2 | Модель робота | ⬜ | 2 |
| 3 | Виртуальный лидар | ⬜ | 1 |
| 4 | Построение карты | ⬜ | 3 |
| 5 | Локализация | ⬜ | 2 |
| 6 | Планирование пути | ⬜ | 2 |
| 7 | Графический интерфейс | ⬜ | 7 |
| 8 | Интеграция | ⬜ | 4 |
| 9 | Тестирование и документация | ⬜ | 6 |

**Всего**: ~37 файлов

---

## 🔗 Полезные ссылки

- [Pygame Documentation](https://www.pygame.org/docs/)
- [NumPy Documentation](https://numpy.org/doc/)
- [A* Algorithm Visualization](https://www.redblobgames.com/pathfinding/a-star/introduction.html)
- [Occupancy Grid Mapping](https://en.wikipedia.org/wiki/Occupancy_grid_mapping)
- [Bresenham's Line Algorithm](https://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm)

---

## 📝 Журнал решений

> Записывай здесь важные решения, отклонения от плана, проблемы и их решения.

| Дата | Фаза | Решение/Проблема |
|------|------|------------------|
| | | |
