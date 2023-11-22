
task = '做一个翻译软件的界面，包括上传文件和选择翻译的语言，语言包括: 英文、中文、日文，默认英文。上传文件后，可以选择翻译的语言，然后点击翻译按钮，文件地址和翻译的语言会传给后端。'

def test__llm_write_ui_lib():
    from GeneralAgent.skills.agent_builder_2 import _llm_write_ui_lib
    code = _llm_write_ui_lib('LibTemplate', task)
    # print(code)
    assert 'antd' in code


def test_create_application_ui():
    from GeneralAgent import skills
    lib_name = 'LibTest'
    lib_name, js_path = skills.create_application_ui(task, component_name=lib_name)
    # 验证js文件存在
    import os
    assert os.path.exists(js_path)
    assert lib_name in js_path


if __name__ == '__main__':
    # test__llm_write_ui_lib()
    test_create_application_ui()