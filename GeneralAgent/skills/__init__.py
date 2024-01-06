# 单列
import os

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
        self._global_cache_dict = {}
        self._load_local_funs()
        self._load_remote_funs()

    def _load_local_funs(self):
        from GeneralAgent.skills.python_envs import load_functions_with_directory
        self._local_funs = {}
        funcs = load_functions_with_directory(os.path.dirname(__file__))
        for fun in funcs:
            self._local_funs[fun.__name__] = fun

    def _load_remote_funs(self):
        from GeneralAgent.utils import get_functions_dir
        from GeneralAgent.skills.python_envs import load_functions_with_directory
        self._remote_funs = {}
        funcs = load_functions_with_directory(get_functions_dir())
        for fun in funcs:
            self._remote_funs[fun.__name__] = fun

    def _search_functions(self, task_description, return_list=False):
        """
        Search functions that may help to solve the task.
        """
        from .llm_inference import search_similar_texts
        signatures = self._all_function_signatures()
        # print(signatures)
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
    
    def _set_cache(self, key, value):
        self._global_cache_dict[key] = value

    def _get_cache(self, key):
        return self._global_cache_dict.get(key, None)

skills = Skills._instance()