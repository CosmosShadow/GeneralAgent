

def test_function_code_generation():
    from GeneralAgent import skills
    task = "返回一个1到1千万间的随机数"
    code = skills.function_code_generation(task)
    print(code)
    assert '10000000' in code

def test_application_code_generation():
    from GeneralAgent import skills
    task = "读取用户上传的文件内容，并返回文件内容"
    code = skills.application_code_generation(task)
    print(code)
    assert 'skills.read_file_content' in code

if __name__ == '__main__':
    test_function_code_generation()
    test_application_code_generation()