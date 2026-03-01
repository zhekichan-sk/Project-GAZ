"""
Главный модуль приложения.
"""

import argparse
import sys
import os
import tkinter as tk

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
        default=None,
        help='Ширина окна (по умолчанию: размер экрана минус отступы)'
    )
    
    parser.add_argument(
        '--height',
        type=int,
        default=None,
        help='Высота окна (по умолчанию: размер экрана минус отступы)'
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
    
    # Размер окна: по умолчанию — экран минус отступы (края чуть меньше границ экрана)
    if args.width is None or args.height is None:
        root = tk.Tk()
        root.withdraw()
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        root.destroy()
        margin = 40  # отступ от краёв экрана в пикселях
        width = args.width if args.width is not None else max(800, screen_w - 2 * margin)
        height = args.height if args.height is not None else max(600, screen_h - 2 * margin)
    else:
        width = args.width
        height = args.height
    
    try:
        # Создаем приложение
        app = Application(config_path=args.config)
        app.setup(width=width, height=height)
        
        # Загрузка карты, если указана
        if args.map and os.path.exists(args.map):
            from src.mapping.occupancy_grid import OccupancyGrid
            app.occupancy_grid = OccupancyGrid.load(args.map)
            app.mapper = None  # Пересоздадим если нужно
            print(f"Карта загружена из {args.map}")
        
        # Запускаем приложение
        app.run(initial_mode=args.mode, width=width, height=height)
        
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

