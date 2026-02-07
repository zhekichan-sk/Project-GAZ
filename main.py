"""
Главный модуль приложения.
"""

import argparse
import sys
import os

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

from src.app import Application


def main():
    """Точка входа в приложение."""
    parser = argparse.ArgumentParser(
        description='Симулятор робота с лидарным картографированием',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python main.py
  python main.py --config configs/demo_maze.json
  python main.py --width 1600 --height 1200 --mode blind
  python main.py --map maps/saved_map.pkl
        """
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Путь к конфигурационному файлу среды'
    )
    
    parser.add_argument(
        '--width',
        type=int,
        default=1500,
        help='Ширина окна (по умолчанию: 1500)'
    )
    
    parser.add_argument(
        '--height',
        type=int,
        default=1200,
        help='Высота окна (по умолчанию: 1200)'
    )
    
    parser.add_argument(
        '--mode',
        type=str,
        choices=['editor', 'blind'],
        default='editor',
        help='Начальный режим: editor (редактор карты) или blind (слепой робот)'
    )
    
    parser.add_argument(
        '--map',
        type=str,
        default=None,
        help='Путь к загружаемой карте (опционально)'
    )
    
    args = parser.parse_args()
    
    try:
        # Создаем приложение
        app = Application(config_path=args.config)
        app.setup()
        
        # Загрузка карты, если указана
        if args.map and os.path.exists(args.map):
            from src.mapping.occupancy_grid import OccupancyGrid
            app.occupancy_grid = OccupancyGrid.load(args.map)
            app.mapper = None  # Пересоздадим если нужно
            print(f"Карта загружена из {args.map}")
        
        # Запускаем приложение
        app.run(initial_mode=args.mode, width=args.width, height=args.height)
        
    except KeyboardInterrupt:
        print("\nПриложение прервано пользователем")
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if 'app' in locals():
            app.cleanup()


if __name__ == "__main__":
    main()

