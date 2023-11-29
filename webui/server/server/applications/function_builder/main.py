
async def main(chat_history, input, file_path, output_callback, file_callback, ui_callback):
    from GeneralAgent.agent import Agent
    from GeneralAgent import skills
    from GeneralAgent.interpreter import RoleInterpreter, PythonInterpreter, FileInterpreter, ShellInterpreter
    from GeneralAgent.utils import get_functions_dir
    function_dir = get_functions_dir()
    role_prompt = f"""
你是一个根据用户需求，编写python函数到文件中的agent.

# 写函数的时候，你应当先搜索可用的函数. For Example
```python
search_functions('scrape web page')
```

# 函数应该写在文件夹 {function_dir} 下，文件名应该是函数名
# 文件内容是函数和函数的测试函数(test_开头)
# import代码应该放在函数内部
比如:

```file
{function_dir}/xxx.py write 0 -1 <<EOF
def xxx(xx)
    import xx
    pass
def test_xxx(xx)
    pass
EOF
```

# 写好的函数可以通过GeneralAgent的skills库来访问，比如:

```python
from GeneralAgent import skills
result = skills.xxx()
skills.test_xxx()
```

# Note:
- Don't make up functions that don't exist

# General process for write function
* Fully communicate needs with users
* search available functions (by search_functions in python)
* edit functions (by file operation)
* test functions (by python)
* ask for test files if needed, for example test data, test code, etc.
"""
    functoins = [
        skills.search_functions,
    ]
    workspace = './'
    agent = Agent(workspace)
    role_interpreter = RoleInterpreter(system_prompt=role_prompt)
    python_interpreter = PythonInterpreter(serialize_path=f'{workspace}/code.bin')
    python_interpreter.function_tools = functoins
    
    # when file operation(python file), reload functions
    file_interpreter = FileInterpreter()
    async def file_callback():
        skills._load_remote_funs()
    
    file_interpreter.outptu_parse_done_recall = file_callback
    agent.interpreters = [role_interpreter, python_interpreter, FileInterpreter(), ShellInterpreter()]
    agent.model_type = 'smart'
    agent.hide_output_parse = False
    await agent.run(input, output_callback=output_callback)