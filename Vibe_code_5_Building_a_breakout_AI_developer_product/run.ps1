# Windows PowerShell版本的运行脚本

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

switch ($Command) {
    "run" {
        Write-Host "启动应用..." -ForegroundColor Green
        $env:PYTHONPATH = "."
        uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
    }
    "test" {
        Write-Host "运行测试..." -ForegroundColor Green
        $env:PYTHONPATH = "."
        pytest -q backend/tests
    }
    "format" {
        Write-Host "格式化代码..." -ForegroundColor Green
        black .
        ruff check . --fix
    }
    "lint" {
        Write-Host "检查代码..." -ForegroundColor Green
        ruff check .
    }
    "seed" {
        Write-Host "初始化数据库..." -ForegroundColor Green
        $env:PYTHONPATH = "."
        python -c "from backend.app.db import apply_seed_if_needed; apply_seed_if_needed()"
    }
    default {
        Write-Host "用法: .\run.ps1 [run|test|format|lint|seed]" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "可用命令:" -ForegroundColor Cyan
        Write-Host "  run     - 启动应用"
        Write-Host "  test    - 运行测试"
        Write-Host "  format  - 格式化代码"
        Write-Host "  lint    - 检查代码"
        Write-Host "  seed    - 初始化数据库"
    }
}




