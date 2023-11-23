

def test_edit_normal_function():
    from GeneralAgent import skills
    fun_name = 'random_big_value'
    task = "返回一个1到1千万间的随机数"
    code = skills.edit_normal_function(fun_name, task)
    # print(code)
    # assert '10000000' in code
    assert fun_name in code

def test_application_code_generation():
    from GeneralAgent import skills
    task = "读取用户上传的文件内容，并返回文件内容"
    code = skills.application_code_generation(task)
    # print(code)
    assert 'skills.read_file_content' in code

def test_search_functions():
    from GeneralAgent import skills
    result = skills.search_functions('translate text')
    print(result)
    assert 'skills.translate_text' in result
    result = skills.search_functions('翻译')
    assert 'skills.translate_text' in result
    print(result)

def test_edit_llm_function():
    from GeneralAgent import skills
    function_name = 'translate_text_test'
    signature = skills.edit_llm_function(function_name, 'Translate text of any length into the specified language.')
    print(signature)
    assert signature.startswith('skills.')
    assert function_name in signature
    skills.delete_function(function_name)


# def test_install_application():
#     import os
#     from GeneralAgent import skills
#     code_dir = skills.get_code_dir()
#     if os.path.exists(code_dir):
#         import shutil
#         shutil.rmtree(code_dir)
#     os.mkdir(code_dir)
#     task = "读取用户上传的文件内容，并返回文件内容"
#     skills.create_application(task)
#     application_id = 'test_application_id'
#     application_name = '读取文件'
#     description = '读取用户上传的文件内容，并返回文件内容'
#     skills.install_application(application_id, application_name, description, upload_file='yes')

if __name__ == '__main__':
    test_edit_normal_function()
    # test_application_code_generation()
    # test_install_application()
    # test_edit_llm_function()
    # test_search_functions()