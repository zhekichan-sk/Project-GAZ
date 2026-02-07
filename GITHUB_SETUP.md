# Инструкция по загрузке на GitHub

## Быстрый старт

1. **Запустите `setup_git.bat`** - это инициализирует git репозиторий и создаст первый коммит

2. **Создайте репозиторий на GitHub:**
   - Перейдите на https://github.com
   - Нажмите "New repository" (зеленая кнопка)
   - Введите название (например: `lidar-robot-simulator`)
   - НЕ добавляйте README, .gitignore или лицензию
   - Нажмите "Create repository"

3. **Подключите локальный репозиторий к GitHub:**

   Откройте командную строку или PowerShell в папке проекта и выполните:

   ```bash
   # Добавьте remote (замените YOUR_USERNAME и REPO_NAME на ваши данные)
   git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
   
   # Переименуйте ветку в main
   git branch -M main
   
   # Загрузите код
   git push -u origin main
   ```

## Альтернативный способ (через GitHub Desktop)

1. Установите GitHub Desktop: https://desktop.github.com/
2. File → Add Local Repository
3. Выберите папку проекта
4. Publish repository
5. Введите название и описание
6. Нажмите "Publish repository"

## Если возникнут проблемы с аутентификацией

GitHub больше не поддерживает пароли для HTTPS. Используйте Personal Access Token:

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. Выберите scope: `repo` (полный доступ к репозиториям)
4. Скопируйте токен
5. При `git push` используйте токен вместо пароля

## Текущий статус проекта

✅ Git репозиторий готов к инициализации (запустите `setup_git.bat`)
✅ Все файлы проекта готовы
✅ README.md создан
✅ .gitignore настроен

## Структура проекта

```
├── main.py                    # Главный модуль
├── run_map.bat               # Скрипт запуска
├── setup_git.bat             # Скрипт инициализации git
├── README.md                 # Описание проекта
├── .gitignore                # Игнорируемые файлы
├── src/                      # Исходный код
│   ├── app.py
│   ├── simulation/           # Симуляция
│   ├── mapping/             # Картографирование
│   ├── localization/        # Локализация
│   ├── navigation/          # Навигация
│   ├── gui/                # Интерфейс
│   └── common/             # Общие модули
└── configs/                 # Конфигурации
```
