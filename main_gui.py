"""
Главный файл для запуска GUI приложения.
"""

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

from src.gui.main_window import main

if __name__ == "__main__":
    main()

