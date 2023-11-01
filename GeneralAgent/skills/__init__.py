# 单列
import os

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

        return [f[1] for f in functions]
    except Exception as e:
        # 代码可能有错误，加载不起来
        import logging
        logging.exception(e)
        return []

class Skills:
    __instance = None

    @classmethod
    def __getInstance(cls):
        return cls.__instance

    @classmethod
    def _instance(cls, *args, **kwargs):
        if not Skills.__instance:
            Skills.__instance = Skills(*args, **kwargs)
        return Skills.__instance
    
    def __setattr__(self, name, value):
        if name.startswith('_'):
            object.__setattr__(self, name, value)
        else:
            raise ValueError('The code should not run')

    def __getattr__(self, name):
        if name.startswith('_'):
            return object.__getattr__(self, name)
        else:
            return self._get_func(name)
        
    def _get_func(self, name):
        return self._funs.get(name, None)
    
    def __init__(self):
        self._funs = {}
        self._load_local_funs()

    def _load_funcs(self, the_dir):
        total_funs = []
        for file in os.listdir(the_dir):
            if file.endswith('.py') and (not file.startswith('__init__') and not file.startswith('_') and not file == 'main.py'):
                funcs = load_functions_with_path(os.path.join(the_dir, file))
                total_funs += funcs
        return total_funs

    def _load_local_funs(self):
        the_dir = os.path.dirname(__file__)
        funcs = self._load_funcs(the_dir)
        self._funs = {}
        for fun in funcs:
            self._funs[fun.__name__] = fun

    def _search_tools(self, task):
        """search tools by task"""
        from .get_function_signature import get_function_signature
        return '\n\n'.join([get_function_signature(fun) for fun in self._funs.values()])

skills = Skills._instance()