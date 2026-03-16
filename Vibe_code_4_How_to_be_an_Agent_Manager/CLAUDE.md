# CLAUDE.md
## Repository Context
- 项目类型：全栈 Web 应用（Python 后端 + 前端）
- 后端目录：`week4/backend/`
- 数据库脚本：`week4/data/seed.sql`
- 测试命令：`cd week4/backend && python -m pytest tests/ -v`
- 文档目录：`week4/docs/`

## Tool Permissions
- 允许执行 Bash 命令（仅限项目目录内）
- 允许读写 `week4/backend/`、`week4/data/`、`week4/docs/` 目录

## Workflow Rules
- 执行 `/init-db-and-test` 时，必须先完成数据库初始化，再运行测试。
- 测试失败时，优先检查 SQL 脚本和测试用例的兼容性。