# 单列
import os
import logging

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
    
    def _skill_consume(self, method_name, amount, money_type='dollar'):
        """
        消费技能: 函数调用时的扣费
        @param method_name: 消费的函数名称
        @param amount: 消费的数量
        @param money_type: 消费的货币类型
        """
        assert money_type in ['dollar', 'rmb']
        try:
            self._local_skill_consume(method_name, amount, money_type)
        except Exception as e:
            logging.exception(e)
            logging.warn('Skill _local_skill_consume function not found')
    
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
        if fun is not None:
            return fun
        if name == 'output':
            return default_output_callback
        logging.error('Function {} not found'.format(name))
        return None
    
    def __init__(self):
        self._local_funs = {}
        self._remote_funs = {}
        self._load_local_funs()
        self._local_funs['input'] = input
        self._local_funs['check'] = default_check
        self._local_funs['print'] = default_output_callback
        self._local_funs['output'] = default_output_callback

    def _load_local_funs(self):
        """
        加载本目录的函数
        """
        from GeneralAgent.skills.python_envs import load_functions_with_directory
        self._local_funs = {}
        funcs = load_functions_with_directory(os.path.dirname(__file__))
        for fun in funcs:
            self._local_funs[fun.__name__] = fun

    def _load_remote_funs(self, functions_code_dir):
        """
        加载远程函数
        @param functions_code_dir: 函数代码目录
        """
        from GeneralAgent.skills.python_envs import load_functions_with_directory
        self._remote_funs = {}
        funcs = load_functions_with_directory(functions_code_dir)
        for fun in funcs:
            self._remote_funs[fun.__name__] = fun

    def _search_functions(self, task_description, return_list=False):
        """
        搜索函数
        @param task_description: 任务描述
        @param return_list: 是否返回列表，默认False，返回字符串s
        """
        from .llm_inference import search_similar_texts
        signatures = self._all_function_signatures()
        results = search_similar_texts(task_description, signatures, top_k=5)
        if return_list:
            return results
        else:
            return '\n'.join(results)

    def _all_function_signatures(self):
        """
        获取所有函数的签名: 本地函数和远程函数
        """
        from .python_envs import get_function_signature
        locals = [get_function_signature(fun, 'skills') for fun in self._local_funs.values() if not fun.__name__.startswith('test_')]
        remotes = [get_function_signature(fun, 'skills') for fun in self._remote_funs.values() if not fun.__name__.startswith('test_')]
        return locals + remotes


skills = Skills._instance()