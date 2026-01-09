"""
Query Tools for Intent Router
Provides date and weather query capabilities.
"""

from datetime import datetime
from typing import Optional
import random


def query_date(location: Optional[str] = None) -> str:
    """
    Query the current date and time.

    Args:
        location: Optional location name (for future timezone support)

    Returns:
        Current date and time information
    """
    try:
        now = datetime.now()
        date_str = now.strftime("%Y年%m月%d日")
        time_str = now.strftime("%H:%M:%S")
        weekday = now.strftime("%A")
        weekday_zh = now.strftime("%A").translate(str.maketrans({
            'Monday': '星期一',
            'Tuesday': '星期二',
            'Wednesday': '星期三',
            'Thursday': '星期四',
            'Friday': '星期五',
            'Saturday': '星期六',
            'Sunday': '星期日'
        }))

        result = f"📅 当前日期时间\n\n"
        result += f"日期: {date_str} ({weekday})\n"
        result += f"时间: {time_str}\n"

        if location:
            result += f"地区: {location}\n"

        return result

    except Exception as e:
        return f"Error querying date: {str(e)}"


def query_weather(city: str) -> str:
    """
    Query weather information for a city.

    Args:
        city: Name of the city to query weather for

    Returns:
        Weather information (simulated/random for demo)
    """
    try:
        # Simulated weather data for demo purposes
        weather_conditions = ["晴", "多云", "阴", "小雨", "大雨", "雪"]
        directions = ["东", "南", "西", "北", "东北", "东南", "西北", "西南"]

        # Random but consistent per city (simple hash)
        city_hash = sum(ord(c) for c in city) % 100
        temp = 10 + (city_hash % 25)  # Temperature between 10-35°C
        humidity = 40 + (city_hash % 50)  # Humidity between 40-90%
        wind_speed = 1 + (city_hash % 10)  # Wind speed between 1-11 m/s
        condition = weather_conditions[city_hash % len(weather_conditions)]
        direction = directions[(city_hash * 2) % len(directions)]

        result = f"🌤️ {city} 天气情况\n\n"
        result += f"天气: {condition}\n"
        result += f"温度: {temp}°C\n"
        result += f"湿度: {humidity}%\n"
        result += f"风向: {direction}风\n"
        result += f"风速: {wind_speed} m/s\n"
        result += f"\n(注: 此为模拟数据，仅用于演示)"

        return result

    except Exception as e:
        return f"Error querying weather: {str(e)}"
