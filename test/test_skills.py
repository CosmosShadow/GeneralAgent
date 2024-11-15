from GeneralAgent.skills.python_envs import python_line_is_variable_expression


def test_python_line_is_variable_expression():
    assert python_line_is_variable_expression("a")
    assert python_line_is_variable_expression("a, b")
    assert python_line_is_variable_expression("a + b")
    assert python_line_is_variable_expression("vars[0]")
    assert python_line_is_variable_expression('scrape_web("https://www.baidu.com")[0]')

    assert python_line_is_variable_expression(" vars[0]") is False
    assert python_line_is_variable_expression("print(a)") is False
    assert python_line_is_variable_expression("x = a + b") is False
