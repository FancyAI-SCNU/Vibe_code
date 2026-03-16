"""
MCP Host: 通过 OpenAI 兼容 API (阿里云百炼 qwen-plus) 驱动 MCP Server 的工具调用。

用法:
    设置环境变量 DASHSCOPE_API_KEY 后运行:
        uv run python host.py                    # 默认连接 weather_mcp.py
        uv run python host.py weather_mcp.py     # 天气 MCP Server
        uv run python host.py simple_mcp.py      # 文件操作 MCP Server

    也可直接在脚本同目录创建 .env 文件:
        DASHSCOPE_API_KEY=sk-xxx
"""

import os
import sys
import json
import asyncio

from dotenv import load_dotenv
from openai import OpenAI
from fastmcp import Client

load_dotenv()

# ── LLM 配置 ────────────────────────────────────────────────
MODEL = "qwen3.5-flash"
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# 根据连接的 MCP Server 选择不同的 system prompt
SYSTEM_PROMPTS = {
    "weather_mcp.py": (
        "你是一个天气助手，可以通过工具查询城市天气信息。"
        "当用户询问天气相关问题时，请调用可用的工具来获取数据并用友好的中文回答。"
        "回答时请包含关键信息如温度、天气状况、风速等，并给出穿衣或出行建议。"
    ),
    "simple_mcp.py": (
        "你是一个有用的编程助手，可以通过工具来读取文件、列出目录和编辑文件。"
        "当用户请求涉及文件操作时，请调用可用的工具来完成任务，然后根据工具返回的结果进行回答。"
    ),
}
DEFAULT_SYSTEM_PROMPT = "你是一个有用的助手，可以通过可用工具来帮助用户完成任务。"


def get_openai_client() -> OpenAI:
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "请设置环境变量 DASHSCOPE_API_KEY，或在 .env 文件中配置。"
        )
    return OpenAI(api_key=api_key, base_url=BASE_URL)


def mcp_tools_to_openai_format(mcp_tools: list) -> list[dict]:
    """将 MCP 工具列表转换为 OpenAI function-calling 格式。"""
    openai_tools = []
    for tool in mcp_tools:
        openai_tools.append({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.inputSchema,
            },
        })
    return openai_tools


async def run_chat():
    """主聊天循环：用户输入 → LLM 生成 → 工具调用 → 返回结果。"""
    llm = get_openai_client()

    # 通过命令行参数选择 MCP Server，默认 weather_mcp.py
    server_script = sys.argv[1] if len(sys.argv) > 1 else "weather_mcp.py"
    system_prompt = SYSTEM_PROMPTS.get(server_script, DEFAULT_SYSTEM_PROMPT)

    # 连接 MCP Server（通过 STDIO 启动对应脚本）
    mcp_client = Client(server_script)

    async with mcp_client:
        # 获取 MCP 工具并转换格式
        mcp_tools = await mcp_client.list_tools()
        openai_tools = mcp_tools_to_openai_format(mcp_tools)

        print("=" * 60)
        print("MCP Host 已启动")
        print(f"MCP Server: {server_script}")
        print(f"模型: {MODEL}")
        print(f"可用工具: {[t.name for t in mcp_tools]}")
        print("输入 'quit' 或 'exit' 退出")
        print("=" * 60)

        messages: list[dict] = [
            {"role": "system", "content": system_prompt},
        ]

        while True:
            # ── 获取用户输入 ──
            try:
                user_input = input("\n你: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n再见！")
                break

            if not user_input:
                continue
            if user_input.lower() in ("quit", "exit"):
                print("再见！")
                break

            messages.append({"role": "user", "content": user_input})

            # ── 调用 LLM（可能多轮工具调用）──
            while True:
                response = llm.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    tools=openai_tools if openai_tools else None,
                )

                choice = response.choices[0]
                assistant_msg = choice.message

                # 把 assistant 消息加入上下文
                messages.append(assistant_msg.model_dump())

                # 如果没有工具调用，直接输出并结束本轮
                if not assistant_msg.tool_calls:
                    print(f"\n助手: {assistant_msg.content}")
                    break

                # ── 执行工具调用 ──
                for tool_call in assistant_msg.tool_calls:
                    fn_name = tool_call.function.name
                    fn_args = json.loads(tool_call.function.arguments)
                    print(f"  [调用工具] {fn_name}({fn_args})")

                    try:
                        result = await mcp_client.call_tool(fn_name, fn_args)
                        # result 是 CallToolResult 对象，通过 .content 获取内容块列表 ***
                        content_blocks = result if isinstance(result, list) else getattr(result, "content", [result])
                        result_text = "\n".join(
                            block.text if hasattr(block, "text") else str(block)
                            for block in content_blocks
                        )
                    except Exception as e:
                        result_text = f"工具调用出错: {e}"

                    print(f"  [工具结果] {result_text[:200]}{'...' if len(result_text) > 200 else ''}")

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result_text,
                    })

                # 继续循环，让 LLM 根据工具结果生成最终回答


if __name__ == "__main__":
    asyncio.run(run_chat())
