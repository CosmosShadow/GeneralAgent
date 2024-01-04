
task = 'Create a user interface that allows users to upload two text files for merging.'

def test_llm_write_ui_lib():
    from GeneralAgent.skills.agent_builder_2 import _llm_write_ui_lib
    code = _llm_write_ui_lib('LibTemplate', task)
    print(code)
    assert 'antd' in code


def test_create_application_ui():
    from GeneralAgent import skills
    lib_name = 'LibTest'
    lib_name, js_path, code = skills.create_application_ui(task, component_name=lib_name)
    # 验证js文件存在
    import os
    js_path = os.path.join(skills.get_code_dir(), js_path)
    assert os.path.exists(js_path)
    assert lib_name in js_path


if __name__ == '__main__':
    test_llm_write_ui_lib()
    test_create_application_ui()