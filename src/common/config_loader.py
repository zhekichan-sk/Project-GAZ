"""
Загрузчик конфигурационных файлов.
"""

import json
import os
from typing import Dict, Any


def load_environment_config(path: str) -> Dict[str, Any]:
    """
    Загружает конфигурацию среды из JSON файла.
    
    Args:
        path: Путь к файлу конфигурации
        
    Returns:
        Словарь с конфигурацией среды
        
    Raises:
        FileNotFoundError: Если файл не найден
        json.JSONDecodeError: Если файл содержит невалидный JSON
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Конфигурационный файл не найден: {path}")
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Ошибка парсинга JSON в файле {path}: {e.msg}",
            e.doc,
            e.pos
        )


def load_robot_config(path: str) -> Dict[str, Any]:
    """
    Загружает конфигурацию робота из JSON файла.
    
    Args:
        path: Путь к файлу конфигурации
        
    Returns:
        Словарь с конфигурацией робота
        
    Raises:
        FileNotFoundError: Если файл не найден
        json.JSONDecodeError: Если файл содержит невалидный JSON
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Конфигурационный файл не найден: {path}")
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Ошибка парсинга JSON в файле {path}: {e.msg}",
            e.doc,
            e.pos
        )


def validate_config(config: Dict[str, Any], schema: str) -> bool:
    """
    Валидирует конфигурацию по заданной схеме.
    
    Args:
        config: Словарь с конфигурацией
        schema: Название схемы валидации ('environment' или 'robot')
        
    Returns:
        True, если конфигурация валидна
        
    Raises:
        ValueError: Если конфигурация не соответствует схеме
    """
    if schema == 'environment':
        required_keys = ['environment', 'obstacles']
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Отсутствует обязательный ключ '{key}' в конфигурации среды")
        
        env = config['environment']
        env_required = ['name', 'width', 'height', 'background_color']
        for key in env_required:
            if key not in env:
                raise ValueError(f"Отсутствует обязательный ключ 'environment.{key}'")
        
        if not isinstance(config['obstacles'], list):
            raise ValueError("'obstacles' должен быть списком")
        
    elif schema == 'robot':
        required_keys = ['robot', 'lidar']
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Отсутствует обязательный ключ '{key}' в конфигурации робота")
        
        robot = config['robot']
        robot_required = ['radius', 'color', 'speed', 'rotation_speed', 'start_position', 'start_angle']
        for key in robot_required:
            if key not in robot:
                raise ValueError(f"Отсутствует обязательный ключ 'robot.{key}'")
        
        lidar = config['lidar']
        lidar_required = ['num_rays', 'max_range', 'fov', 'noise_std', 'angle_resolution']
        for key in lidar_required:
            if key not in lidar:
                raise ValueError(f"Отсутствует обязательный ключ 'lidar.{key}'")
    else:
        raise ValueError(f"Неизвестная схема валидации: {schema}")
    
    return True

