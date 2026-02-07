@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo Инициализация Git репозитория...
if exist .git (
    echo Удаление старого репозитория...
    rmdir /s /q .git
)
git init
echo Добавление файлов...
git add .gitignore README.md GITHUB_SETUP.md main.py run_map.bat setup_git.bat
git add src/
git add configs/
echo Создание коммита...
git commit -m "Initial commit: Симулятор робота с лидаром"
echo.
echo Git репозиторий готов!
echo.
echo Следующие шаги:
echo 1. Создайте репозиторий на GitHub
echo 2. Выполните команды из файла GITHUB_SETUP.md
echo.
pause

