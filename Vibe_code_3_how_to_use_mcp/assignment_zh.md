# 第3周 Assignment — 构建自定义MCP服务器

设计并实现一个Model Context Protocol (MCP)服务器，封装真实的外部API。你可以选择：

- **本地运行**（STDIO传输），并与MCP客户端（如Claude Desktop）集成。
- 或**远程运行**（HTTP传输），并从模型代理或客户端调用。这更难但可获得额外学分。

为符合MCP授权规范，添加认证机制（API密钥或OAuth2）可获得额外加分。

## 学习目标

- 理解MCP核心功能：工具、资源、提示词。
- 实现带类型参数和健壮错误处理的工具定义。
- 遵循日志记录和传输最佳实践（STDIO服务器不要使用stdout）。
- （可选）为HTTP传输实现授权流程。

## 要求

1. 选择一个外部API，并说明将使用的端点（示例：天气、GitHub Issues、Notion页面、影视数据库、日历、任务管理器、金融/加密货币、旅行、体育数据等）。
2. 暴露至少两个MCP工具。
3. 实现基本弹性：
   - 对HTTP失败、超时和空结果进行优雅错误处理。
   - 尊重API速率限制（例如简单退避或用户可见警告）。
4. 打包与文档：
   - 提供清晰的设置说明、环境变量和运行命令。
   - 包含示例调用流程（在客户端中输入/点击什么来触发工具）。
5. 选择一种部署模式：
   - 本地：STDIO服务器，可在你的机器上运行，并能被Claude Desktop或Cursor等AI IDE发现。
   - 远程：可通过网络访问的HTTP服务器，可被MCP感知客户端或代理运行时调用。如已部署且可访问，可获额外学分。
6. （可选）加分项：认证
   - 通过环境变量和客户端配置支持API密钥；或
   - 为HTTP传输实现OAuth2式承载令牌，验证令牌受众且不将令牌传递给上游API。

## 交付成果

- `week3/`目录下的源代码（建议：`week3/server/`目录，包含清晰入口点如 `main.py`或 `app.py`）。
- `week3/README.md`文件，包含：
  - 先决条件、环境设置和运行说明（本地和/或远程）。
  - 如何配置MCP客户端（本地使用Claude Desktop示例）或远程代理运行时。
  - 工具参考：名称、参数、示例输入/输出及预期行为。

## 评分标准（共90分）

- 功能性（35分）：实现2+个工具，正确API集成，有意义的输出。
- 可靠性（20分）：输入验证、错误处理、日志记录、速率限制意识。
- 开发者体验（20分）：清晰的设置/文档，易于本地运行；合理的文件夹结构。
- 代码质量（15分）：可读代码、描述性命名、最小复杂度、适用处添加类型提示。
- 额外学分（10分）：
  - +5分：远程HTTP MCP服务器，可被OpenAI/Claude SDK等代理/客户端调用。
  - +5分：正确实现认证（API密钥或OAuth2+受众验证）。

## 有用参考资料

- MCP服务器快速入门：[modelcontextprotocol.io/quickstart/server](https://modelcontextprotocol.io/quickstart/server)。
  *注意：你不能提交此确切示例。*
- MCP授权（HTTP）：[modelcontextprotocol.io/specification/2025-06-18/basic/authorization](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)
- Cloudflare上的远程MCP（代理）：[developers.cloudflare.com/agents/guides/remote-mcp-server/](https://developers.cloudflare.com/agents/guides/remote-mcp-server/)。在部署前，使用modelcontextprotocol检查工具在本地调试服务器。
- https://vercel.com/docs/mcp/deploy-mcp-servers-to-vercel 如果选择远程MCP部署，Vercel是不错的选择，提供免费套餐。

## 你需要完成的任务总结

1. 选择一个外部API（如天气、GitHub、Notion等）并确定要使用的端点
2. 实现至少两个MCP工具来封装该API
3. 添加错误处理和弹性机制（超时、空响应、速率限制）
4. 编写清晰的README.md文档，包含设置说明和使用示例
5. 选择本地(STDIO)或远程(HTTP)部署方式并实现
6. （可选）添加API密钥或OAuth2认证
7. 确保代码结构清晰，包含类型提示和良好注释
8. 测试所有功能并确保能与MCP客户端正常交互

## 参考链接

1. https://open.mcd.cn/mcp/doc
2. https://code.visualstudio.com/docs/copilot/customization/mcp-servers
3. https://github.com/cline/cline/issues/3315#issuecomment-3114091526
4. https://zhuanlan.zhihu.com/p/1932083718639563855
