"""快速测试 MCP Server 连接是否正常。"""

import asyncio
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

MCP_URL = "https://mcp.mcd.cn"
TOKEN = "ZqqPFzKDNSVEjdEQvcNnMOSA1cgqMH6H"


async def test():
    transport = StreamableHttpTransport(
        url=MCP_URL,
        headers={"Authorization": f"Bearer {TOKEN}"},
    )
    client = Client(transport)

    try:
        async with client:
            print("✅ 连接成功！")

            tools = await client.list_tools()
            if tools:
                print(f"\n可用工具 ({len(tools)} 个):")
                for t in tools:
                    print(f"  - {t.name}: {t.description or '(无描述)'}")
            else:
                print("⚠️ 连接成功但没有可用工具")

    except Exception as e:
        print(f"❌ 连接失败: {type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(test())
