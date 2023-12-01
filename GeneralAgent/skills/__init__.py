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

        # 过滤functions中以下划线开头的函数、test_开头的函数
        functions = filter(lambda f: not f[0].startswith('_'), functions)
        # functions = filter(lambda f: not f[0].startswith('test_'), functions)

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
            self._local_funs[name] = value

    def __getattr__(self, name):
        if name.startswith('_'):
            return object.__getattr__(self, name)
        else:
            return self._get_func(name)
        
    def _get_func(self, name):
        fun = self._local_funs.get(name, None)
        if fun is not None:
            return fun
        fun = self._remote_funs.get(name, None)
        if fun is not None:
            return fun
        self._load_remote_funs()
        fun = self._remote_funs.get(name, None)
        if fun is not None:
            return fun
        print('Function {} not found'.format(name))
        return None
    
    def __init__(self):
        self._local_funs = {}
        self._remote_funs = {}
        self._load_local_funs()
        self._load_remote_funs()

    def _load_funcs(self, the_dir):
        total_funs = []
        for file in os.listdir(the_dir):
            # 如果file是文件夹
            if os.path.isdir(os.path.join(the_dir, file)):
                total_funs += self._load_funcs(os.path.join(the_dir, file))
            else:
                # 如果file是文件
                if file.endswith('.py') and (not file.startswith('__init__') and not file.startswith('_') and not file == 'main.py'):
                    funcs = load_functions_with_path(os.path.join(the_dir, file))
                    total_funs += funcs
        return total_funs

    def _load_local_funs(self):
        self._local_funs = {}
        funcs = self._load_funcs(os.path.dirname(__file__))
        for fun in funcs:
            self._local_funs[fun.__name__] = fun

    def _load_remote_funs(self):
        from GeneralAgent.utils import get_functions_dir
        self._remote_funs = {}
        funcs = self._load_funcs(get_functions_dir())
        for fun in funcs:
            self._remote_funs[fun.__name__] = fun

    def _search_functions(self, task_description, return_list=False):
        """
        Search functions that may help to solve the task.
        """
        from .llm_inference import search_similar_texts
        signatures = self._all_function_signatures()
        results = search_similar_texts(task_description, signatures, top_k=5)
        if return_list:
            return results
        else:
            return '\n'.join(results)
    
    def _all_function_signatures(self):
        from .python_envs import get_function_signature
        locals = [get_function_signature(fun, 'skills') for fun in self._local_funs.values() if not fun.__name__.startswith('test_')]
        remotes = [get_function_signature(fun, 'skills') for fun in self._remote_funs.values() if not fun.__name__.startswith('test_')]
        return locals + remotes

skills = Skills._instance()