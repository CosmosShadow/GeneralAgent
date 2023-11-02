from .python_interpreter import PythonInterpreter

class AsyncPythonInterpreter(PythonInterpreter):

    def run_code(self, code):
        code = self.add_print(code)
        code = self.import_code + '\n' + code
        globals_backup = self.load()
        logging.debug(code)
        sys_stdout = ''
        output = io.StringIO()
        sys.stdout = output
        success = False
        try:
            exec(code, self.globals)
            success = True
        except Exception as e:
            import traceback
            sys_stdout += traceback.format_exc()
            self.globals = globals_backup
        finally:
            sys_stdout += output.getvalue()
            sys.stdout = sys.__stdout__
        if success:
            self.save()
        sys_stdout = sys_stdout.strip()
        if sys_stdout == '':
            sys_stdout = 'run successfully'
        return sys_stdout
    

# 参考代码

# code1 = """
# a = 10
# """

# code2 = """
# print('code2: a = ', a)
# x = 100
# await asyncio.sleep(1)
# print(x)
# """

# def _remove_unpickleable(namespace):
#     import pickle
#     if '__builtins__' in namespace:
#         namespace.__delitem__('__builtins__')
#     keys = list(namespace.keys())
#     for key in keys:
#         try:
#             pickle.dumps(namespace[key])
#         except Exception as e:
#             namespace.__delitem__(key)
#     return namespace


# def code_wrap(code, namespace):
#     lines = code.split('\n')
#     code = '\n    '.join(lines)
#     variables = '\n    '.join([f'{name} = globals()[\'{name}\']' for name, value in namespace.items()])
#     content = f"""
# import asyncio

# def _remove_unpickleable(namespace):
#     import pickle
#     if '__builtins__' in namespace:
#         namespace.__delitem__('__builtins__')
#     keys = list(namespace.keys())
#     for key in keys:
#         try:
#             pickle.dumps(namespace[key])
#         except Exception as e:
#             namespace.__delitem__(key)
#     for name in ['__name', '__value', '__namespace']:
#         if name in namespace:
#             namespace.__delitem__(name)
#     return namespace

# __namespace = None

# async def __main():
#     {variables}
#     {code}
#     global __namespace
#     __namespace = _remove_unpickleable(locals().copy())
# """
#     # print('----------<code>--------')
#     # print(content)
#     # print('----------</code>--------')
#     return content

# async def main():
#     local_vars = {}
#     code = code_wrap(code1, local_vars)
#     # print(code)
#     exec(code, local_vars, local_vars)
#     foo = local_vars['__main']
#     task = asyncio.create_task(foo())
#     await task

#     local_vars = _remove_unpickleable(local_vars)
#     local_vars = local_vars['__namespace']
#     print(local_vars)

#     code = code_wrap(code2, local_vars)
#     exec(code, local_vars, local_vars)
#     foo = local_vars['__main']
#     task = asyncio.create_task(foo())
#     await task

#     local_vars = _remove_unpickleable(local_vars)
#     local_vars = local_vars['__namespace']
#     print(local_vars)

# if __name__ == '__main__':
#     asyncio.run(main())