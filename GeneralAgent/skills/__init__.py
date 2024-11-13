# 单列
import os
from codyer import skills

def default_output_callback(token):
    if token is not None:
        print(token, end='', flush=True)
    else:
        print('\n', end='', flush=True)


def default_check(check_content=None):
    show = '确认 | 继续 (回车, yes, y, 是, ok) 或者 直接输入你的想法\n'
    if check_content is not None:
        show = f'{check_content}\n\n{show}'
    response = input(show)
    if response.lower() in ['', 'yes', 'y', '是', 'ok']:
        return None
    else:
        return response

def load_functions_with_path(python_code_path) -> (list, str):
    """
    Load functions from python file
    @param python_code_path: the path of python file
    @return: a list of functions and error message (if any, else None)
    """
    try:
        import importlib.util
        import inspect

        # 指定要加载的文件路径和文件名
        module_name = 'skills'
        module_file = python_code_path

        # 使用importlib加载文件
        spec = importlib.util.spec_from_file_location(module_name, module_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # 获取文件中的所有函数
        functions = inspect.getmembers(module, inspect.isfunction)

        # 过滤functions中以下划线开头的函数
        functions = filter(lambda f: not f[0].startswith('_'), functions)

        return [f[1] for f in functions], None
    except Exception as e:
        # 代码可能有错误，加载不起来
        import logging
        logging.exception(e)
        return [], str(e)
    

def load_functions_with_directory(python_code_dir) -> list:
    """
    Load functions from python directory (recursively)
    @param python_code_dir: the path of python directory
    @return: a list of functions
    """
    import os
    total_funs = []
    for file in os.listdir(python_code_dir):
        # if file is directory
        if os.path.isdir(os.path.join(python_code_dir, file)):
            total_funs += load_functions_with_directory(os.path.join(python_code_dir, file))
        else:
            # if file is file
            if file.endswith('.py') and (not file.startswith('__init__') and not file.startswith('_') and not file == 'main.py'):
                funcs, error = load_functions_with_path(os.path.join(python_code_dir, file))
                total_funs += funcs
    return total_funs

if len(skills._functions) == 0:
    skills._add_function('input', input)
    skills._add_function('check', default_check)
    skills._add_function('print', default_output_callback)
    skills._add_function('output', default_output_callback)
    funcs = load_functions_with_directory(os.path.dirname(__file__))
    for fun in funcs:
        skills._add_function(fun.__name__, fun)