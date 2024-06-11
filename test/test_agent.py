from GeneralAgent import Agent

def test_math():
    """数学计算测试. 使用run直接返回python表达式的值"""
    agent = Agent()
    result = agent.run('calculate 0.99 ** 1000, return a float', return_type=float)
    assert 4.317124741065786e-05 == result

def test_function():
    """函数调用测试"""
    def get_weather(city: str) -> str:
        """
        get weather information
        @city: str, city name
        @return: str, weather information
        """
        return f"{city} weather: sunny"
    agent = Agent('你是一个天气小助手', functions=[get_weather])
    result = agent.user_input('成都天气怎么样？')
    assert '晴' in result or 'sunny' in result

if __name__ == '__main__':
    test_math()
    test_function()