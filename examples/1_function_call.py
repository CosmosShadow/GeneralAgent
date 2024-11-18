# 函数调用
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
    handlers=[logging.StreamHandler()],
)
from GeneralAgent import Agent
from dotenv import load_dotenv

load_dotenv()


# 函数: 获取天气信息
def get_weather(city: str) -> str:
    """
    get weather information
    @city: str, city name
    @return: str, weather information
    """
    # return f"{city} weather: sunny"
    weather = "sunny"
    print(f"{city} weather: {weather}")
    return weather


# agent = Agent('你是一个天气小助手', functions=[get_weather], model='deepseek-chat')
agent = Agent("你是一个天气小助手", functions=[get_weather])
agent.user_input("成都天气怎么样？")

# 输出
# ```python
# city = "成都"
# weather_info = get_weather(city)
# weather_info
# ```
# 成都的天气是晴天。
# 请问还有什么我可以帮忙的吗？
