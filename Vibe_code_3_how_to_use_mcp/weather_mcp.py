"""
天气 MCP Server — 封装 Open-Meteo 免费天气 API。

提供 3 个 MCP 工具：
  1. search_city        — 根据城市名搜索坐标（支持中英文）
  2. get_current_weather — 获取指定城市的当前天气
  3. get_weather_forecast — 获取指定城市未来多天天气预报

外部 API：
  - Geocoding: https://geocoding-api.open-meteo.com/v1/search
  - Weather:   https://api.open-meteo.com/v1/forecast

运行：
    uv run python weather_mcp.py
"""

import time
import logging
from typing import Any, Dict, List, Optional

import httpx
from fastmcp import FastMCP

# ── 日志配置（STDIO 模式下只写 stderr）──────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("weather_mcp")

# ── MCP Server ──────────────────────────────────────────────
mcp = FastMCP(name="WeatherMCPServer")

# ── 常量 ────────────────────────────────────────────────────
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
HTTP_TIMEOUT = 15  # 秒
MAX_RETRIES = 2
RETRY_DELAY = 1  # 秒

# WMO 天气代码 → 中文描述
WMO_WEATHER_CODES: Dict[int, str] = {
    0: "晴天",
    1: "大部晴朗",
    2: "局部多云",
    3: "阴天",
    45: "雾",
    48: "雾凇",
    51: "小毛毛雨",
    53: "中毛毛雨",
    55: "大毛毛雨",
    56: "冻毛毛雨（轻）",
    57: "冻毛毛雨（重）",
    61: "小雨",
    63: "中雨",
    65: "大雨",
    66: "冻雨（轻）",
    67: "冻雨（重）",
    71: "小雪",
    73: "中雪",
    75: "大雪",
    77: "雪粒",
    80: "小阵雨",
    81: "中阵雨",
    82: "大阵雨",
    85: "小阵雪",
    86: "大阵雪",
    95: "雷暴",
    96: "雷暴伴小冰雹",
    99: "雷暴伴大冰雹",
}


def _weather_description(code: int) -> str:
    """将 WMO 天气代码转为中文描述。"""
    return WMO_WEATHER_CODES.get(code, f"未知天气（代码 {code}）")


def _http_get(url: str, params: dict) -> dict:
    """
    带重试和超时的 HTTP GET 请求。
    遇到网络异常或 5xx 错误会重试 MAX_RETRIES 次。
    """
    last_error: Optional[Exception] = None
    for attempt in range(1, MAX_RETRIES + 2):  # 1 次原始 + MAX_RETRIES 次重试
        try:
            logger.info("HTTP GET %s (attempt %d) params=%s", url, attempt, params)
            with httpx.Client(timeout=HTTP_TIMEOUT) as client:
                resp = client.get(url, params=params)

            if resp.status_code >= 500:
                raise httpx.HTTPStatusError(
                    f"服务端错误 {resp.status_code}",
                    request=resp.request,
                    response=resp,
                )

            resp.raise_for_status()
            return resp.json()

        except (httpx.TimeoutException, httpx.ConnectError, httpx.HTTPStatusError) as e:
            last_error = e
            logger.warning("请求失败 (attempt %d/%d): %s", attempt, MAX_RETRIES + 1, e)
            if attempt <= MAX_RETRIES:
                time.sleep(RETRY_DELAY * attempt)  # 简单递增退避

    raise RuntimeError(f"请求失败，已重试 {MAX_RETRIES} 次: {last_error}")


# ═══════════════════════════════════════════════════════════
#  工具 1：搜索城市
# ═══════════════════════════════════════════════════════════
@mcp.tool
def search_city(name: str, count: int = 5) -> Dict[str, Any]:
    """
    根据城市名称搜索地理位置，返回匹配的城市列表（含经纬度）。
    支持中文和英文城市名。
    :param name: 城市名称，如 "北京"、"Shanghai"、"Tokyo"。
    :param count: 返回结果数量上限，默认 5。
    :return: 匹配的城市列表。
    """
    if not name or not name.strip():
        return {"status": "❌ 错误", "message": "城市名称不能为空"}

    try:
        data = _http_get(GEOCODING_URL, {"name": name.strip(), "count": count, "language": "zh"})
    except RuntimeError as e:
        return {"status": "❌ 请求失败", "message": str(e)}

    results = data.get("results", [])
    if not results:
        return {"status": "⚠️ 未找到", "message": f"未找到与 '{name}' 匹配的城市"}

    cities = []
    for r in results:
        cities.append({
            "name": r.get("name", ""),
            "country": r.get("country", ""),
            "admin1": r.get("admin1", ""),  # 省/州
            "latitude": r.get("latitude"),
            "longitude": r.get("longitude"),
            "timezone": r.get("timezone", ""),
        })

    return {
        "status": "❤ 搜索城市成功",
        "query": name,
        "count": len(cities),
        "cities": cities,
    }


# ═══════════════════════════════════════════════════════════
#  工具 2：获取当前天气
# ═══════════════════════════════════════════════════════════
@mcp.tool
def get_current_weather(city: str) -> Dict[str, Any]:
    """
    获取指定城市的当前天气信息（温度、风速、湿度等）。
    会自动根据城市名搜索坐标，然后查询天气。
    :param city: 城市名称，如 "北京"、"上海"、"广州"。
    :return: 当前天气信息。
    """
    if not city or not city.strip():
        return {"status": "❌ 错误", "message": "城市名称不能为空"}

    # 先搜索城市获取坐标
    geo_result = search_city(city, count=1)
    if "❤" not in geo_result.get("status", ""):
        return geo_result  # 搜索失败，直接返回错误

    location = geo_result["cities"][0]
    lat, lon = location["latitude"], location["longitude"]

    try:
        weather_data = _http_get(FORECAST_URL, {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,"
                       "weather_code,wind_speed_10m,wind_direction_10m,"
                       "surface_pressure",
            "timezone": "auto",
        })
    except RuntimeError as e:
        return {"status": "❌ 天气请求失败", "message": str(e)}

    current = weather_data.get("current", {})
    if not current:
        return {"status": "⚠️ 无数据", "message": "未获取到当前天气数据"}

    return {
        "status": "❤ 获取当前天气成功",
        "city": location["name"],
        "country": location["country"],
        "admin1": location["admin1"],
        "time": current.get("time", ""),
        "weather": _weather_description(current.get("weather_code", -1)),
        "temperature_c": current.get("temperature_2m"),
        "feels_like_c": current.get("apparent_temperature"),
        "humidity_percent": current.get("relative_humidity_2m"),
        "wind_speed_kmh": current.get("wind_speed_10m"),
        "wind_direction_deg": current.get("wind_direction_10m"),
        "pressure_hpa": current.get("surface_pressure"),
    }


# ═══════════════════════════════════════════════════════════
#  工具 3：获取天气预报
# ═══════════════════════════════════════════════════════════
@mcp.tool
def get_weather_forecast(city: str, days: int = 3) -> Dict[str, Any]:
    """
    获取指定城市未来若干天的天气预报。
    :param city: 城市名称，如 "北京"、"深圳"。
    :param days: 预报天数，1~7 天，默认 3 天。
    :return: 每日天气预报列表。
    """
    if not city or not city.strip():
        return {"status": "❌ 错误", "message": "城市名称不能为空"}

    days = max(1, min(days, 7))  # 限制在 1-7 天

    # 先搜索城市获取坐标
    geo_result = search_city(city, count=1)
    if "❤" not in geo_result.get("status", ""):
        return geo_result

    location = geo_result["cities"][0]
    lat, lon = location["latitude"], location["longitude"]

    try:
        weather_data = _http_get(FORECAST_URL, {
            "latitude": lat,
            "longitude": lon,
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,"
                     "apparent_temperature_max,apparent_temperature_min,"
                     "precipitation_sum,wind_speed_10m_max,"
                     "sunrise,sunset",
            "timezone": "auto",
            "forecast_days": days,
        })
    except RuntimeError as e:
        return {"status": "❌ 天气请求失败", "message": str(e)}

    daily = weather_data.get("daily", {})
    dates = daily.get("time", [])
    if not dates:
        return {"status": "⚠️ 无数据", "message": "未获取到天气预报数据"}

    forecast = []
    for i, date in enumerate(dates):
        forecast.append({
            "date": date,
            "weather": _weather_description(daily["weather_code"][i]),
            "temp_max_c": daily["temperature_2m_max"][i],
            "temp_min_c": daily["temperature_2m_min"][i],
            "feels_like_max_c": daily["apparent_temperature_max"][i],
            "feels_like_min_c": daily["apparent_temperature_min"][i],
            "precipitation_mm": daily["precipitation_sum"][i],
            "wind_max_kmh": daily["wind_speed_10m_max"][i],
            "sunrise": daily["sunrise"][i],
            "sunset": daily["sunset"][i],
        })

    return {
        "status": "❤ 获取天气预报成功",
        "city": location["name"],
        "country": location["country"],
        "admin1": location["admin1"],
        "days": len(forecast),
        "forecast": forecast,
    }


if __name__ == "__main__":
    mcp.run()
