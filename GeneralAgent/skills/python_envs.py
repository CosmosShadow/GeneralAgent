
def get_current_env_python_libs() -> str:
    """
    Return the python libs that installed in current env
    """
    import os
    requirements_path = os.path.join(os.path.dirname(__file__), '../../requirements.txt')
    with open(requirements_path, 'r') as f:
        requirements = f.read()
        requirements = requirements.replace('\n', ' ')
        return requirements.strip()
    

def get_python_version() -> str:
    """
    Return the python version, like "3.8"
    """
    return '3.8'


def get_python_code(content:str) -> str:
    """
    Return the python code text from content
    """
    template = '```python\n(.*?)\n```'
    import re
    code = re.findall(template, content, re.S)
    if len(code) > 0:
        return code[0]
    else:
        return content


def load_functions_with_path(python_code_path):
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
    
def get_function_signature(func, module:str=None):
    """Returns a description string of function"""
    import inspect
    sig = inspect.signature(func)
    sig_str = str(sig)
    desc = f"{func.__name__}{sig_str}"
    if func.__doc__:
        desc += ': ' + func.__doc__.strip()
    if module is not None:
        desc = f'{module}.{desc}'
    if inspect.iscoroutinefunction(func):
        desc = "async " + desc
    return desc