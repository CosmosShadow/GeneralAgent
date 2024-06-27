# 函数调用
from GeneralAgent import Agent

# 函数: 获取天气信息
def get_weather(city: str) -> str:
    """
    get weather information
    @city: str, city name
    @return: str, weather information
    """
    # return f"{city} weather: sunny"
    print(f"{city} weather: sunny")


agent = Agent('你是一个天气小助手', functions=[get_weather])
agent.user_input('成都天气怎么样？')

# 输出
# ```python
# city = "成都"
# weather_info = get_weather(city)
# weather_info
# ```
# 成都的天气是晴天。
# 请问还有什么我可以帮忙的吗？