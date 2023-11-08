
def test_generate_llm_task_function():
    from GeneralAgent import skills
    code = skills.generate_llm_task_function('Translate text of any length into the specified language.')
    print(code)
    # TODO: 直接调用该函数来运行代码
    assert code.startwith('def :')

if __name__ == '__main__':
    test_generate_llm_task_function()
