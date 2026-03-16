# Week 3 — Weather MCP Server

封装 [Open-Meteo](https://open-meteo.com/) 免费天气 API 的 MCP 服务器，支持城市搜索、当前天气查询和多日天气预报。

## 先决条件

- Python ≥ 3.10
- [uv](https://docs.astral.sh/uv/) 包管理器
- （可选）阿里云百炼 API Key（用于 `host.py` 交互模式）

## 环境设置

```bash
# 进入项目目录
cd week3

# 安装依赖（已在项目根目录 pyproject.toml 中配置）
uv sync
```

如需使用 `host.py` 交互模式，创建 `.env` 文件：

```
DASHSCOPE_API_KEY=sk-xxx
```

## 运行方式

### 1. 直接启动 MCP Server（STDIO 模式）

```bash
uv run python weather_mcp.py
```

### 2. 通过 Host 交互（LLM 驱动工具调用）

```bash
# 连接天气 MCP Server（默认）
uv run python host.py

# 也可指定其他 MCP Server
uv run python host.py simple_mcp.py
```

### 3. 在 VS Code Copilot 中使用

项目已配置 `.vscode/mcp.json`，在 VS Code 中：

1. `Ctrl+Shift+P` → `MCP: List Servers`
2. 找到 `weather-mcp`，点击 **Start**
3. 在 Copilot Chat 中切换到 **Agent 模式**
4. 对话中即可触发天气工具调用

## 工具参考

### `search_city`

根据城市名搜索地理位置坐标。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | ✅ | 城市名称（支持中英文） |
| `count` | int | ❌ | 返回结果数量上限，默认 5 |

**示例输入：**
```json
{"name": "北京", "count": 3}
```

**示例输出：**
```json
{
  "status": "❤ 搜索城市成功",
  "query": "北京",
  "count": 1,
  "cities": [
    {
      "name": "北京市",
      "country": "中国",
      "admin1": "北京市",
      "latitude": 39.9075,
      "longitude": 116.39723,
      "timezone": "Asia/Shanghai"
    }
  ]
}
```

### `get_current_weather`

获取指定城市的当前天气信息。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `city` | string | ✅ | 城市名称 |

**示例输入：**
```json
{"city": "上海"}
```

**示例输出：**
```json
{
  "status": "❤ 获取当前天气成功",
  "city": "上海市",
  "country": "中国",
  "time": "2026-02-28T15:00",
  "weather": "局部多云",
  "temperature_c": 12.5,
  "feels_like_c": 10.2,
  "humidity_percent": 65,
  "wind_speed_kmh": 15.3,
  "pressure_hpa": 1018.5
}
```

### `get_weather_forecast`

获取指定城市未来若干天的天气预报。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `city` | string | ✅ | 城市名称 |
| `days` | int | ❌ | 预报天数，1-7，默认 3 |

**示例输入：**
```json
{"city": "广州", "days": 5}
```

**示例输出：**
```json
{
  "status": "❤ 获取天气预报成功",
  "city": "广州市",
  "country": "中国",
  "days": 5,
  "forecast": [
    {
      "date": "2026-02-28",
      "weather": "小雨",
      "temp_max_c": 18.2,
      "temp_min_c": 13.1,
      "precipitation_mm": 2.5,
      "wind_max_kmh": 20.1,
      "sunrise": "06:48",
      "sunset": "18:22"
    }
  ]
}
```

## 外部 API 说明

本项目使用 [Open-Meteo](https://open-meteo.com/) 提供的免费 API，**无需 API Key**：

| API | 端点 | 用途 |
|-----|------|------|
| Geocoding API | `https://geocoding-api.open-meteo.com/v1/search` | 城市名称 → 经纬度 |
| Forecast API | `https://api.open-meteo.com/v1/forecast` | 经纬度 → 天气数据 |

## 弹性处理

- **超时**：HTTP 请求 15 秒超时
- **重试**：网络异常或 5xx 错误自动重试 2 次，递增退避
- **输入校验**：空参数提前返回错误信息
- **空结果处理**：API 无数据时返回友好提示

## 文件结构

```
week3/
├── weather_mcp.py         # 天气 MCP Server（主入口）
├── simple_mcp.py          # 文件操作 MCP Server
├── host.py                # LLM 驱动的交互式 Host
├── test_mcp_connection.py # MCP 连接测试脚本
├── .env                   # 环境变量（需自行创建）
├── README.md              # 本文件
├── assignment.md          # 作业要求（英文）
└── assignment_zh.md       # 作业要求（中文）
```
