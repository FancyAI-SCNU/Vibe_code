@echo off
REM Windows版本的运行脚本

if "%1"=="run" (
    echo 启动应用...
    set PYTHONPATH=.
    uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
) else if "%1"=="test" (
    echo 运行测试...
    set PYTHONPATH=.
    pytest -q backend/tests
) else if "%1"=="format" (
    echo 格式化代码...
    black .
    ruff check . --fix
) else if "%1"=="lint" (
    echo 检查代码...
    ruff check .
) else if "%1"=="seed" (
    echo 初始化数据库...
    set PYTHONPATH=.
    python -c "from backend.app.db import apply_seed_if_needed; apply_seed_if_needed()"
) else (
    echo 用法: run.bat [run^|test^|format^|lint^|seed]
    echo.
    echo 可用命令:
    echo   run     - 启动应用
    echo   test    - 运行测试
    echo   format  - 格式化代码
    echo   lint    - 检查代码
    echo   seed    - 初始化数据库
)




