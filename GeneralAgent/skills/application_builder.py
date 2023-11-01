
def _get_code_dir():
    CODE_DIR = './code'
    return CODE_DIR

def create_function(func_name, task):
    """
    Create a function by task
    """
    # from GeneralAgent import skills
    import os
    code = function_code_generation(task)
    file_path = os.path.join(_get_code_dir(), func_name + '.py')
    with open(file_path, 'w') as f:
        f.write(code)

def delete_function(func_name):
    """
    Delete a function by name
    """
    import os
    file_path = os.path.join(_get_code_dir(), func_name + '.py')
    if os.path.exists(file_path):
        os.remove(file_path)

def list_functions():
    """list all functions, return function names and description"""
    # TODO function description
    import os
    files = os.listdir(_get_code_dir())
    functions = [x.split('.')[0] for x in files]
    return functions

def show_function(func_name):
    import os
    file_path = os.path.join(_get_code_dir(), func_name + '.py')
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            code = f.read()
        return code
    else:
        return None

def update_function(func_name:str, task:str):
    """
    Update a function by task(string)
    """
    import os
    file_path = os.path.join(_get_code_dir(), func_name + '.py')
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            code = f.read()
        code = function_code_generation(task, default_code=code)
        with open(file_path, 'w') as f:
            f.write(code)
    else:
        create_function(func_name, task)


def create_application(task:str):
    """
    Create a application by task
    """
    import os
    code = application_code_generation(task)
    code_path = os.path.join(_get_code_dir(),  'main.py')
    with open(code_path, 'w') as f:
        f.write(code)
    # TODO add application to chat bot

def update_application(task):
    import os
    code_path = os.path.join(_get_code_dir(),  'main.py')
    old_code = ''
    if os.path.exists(code_path):
        with open(code_path, 'r') as f:
            old_code = f.read()
    code = application_code_generation(task, default_code=old_code)
    with open(code_path, 'w') as f:
        f.write(code)


def delete_application():
    import os
    code_path = os.path.join(_get_code_dir(),  'main.py')
    if os.path.exists(code_path):
        os.remove(code_path)

def install_application(application_id, application_name, description, upload_file='yes'):
    # TODO: check function_id and application_name
    import os
    app_json = {
        "id": application_id,
        "name": application_name,
        "description": description,
        "upload_file": upload_file
    }
    bot_json_path = os.path.join(_get_code_dir(), 'bot.json')
    with open(bot_json_path, 'w') as f:
        f.write(app_json)
    # move code to bot
    target_dir = os.path.join(os.path.dirname(__file__), f'../../webui/server/server/application/{application_id}/')
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    os.system(f"mv {_get_code_dir()}/* {target_dir}")


def function_code_generation(task, default_code=None):
    """Return the python function code text that completes the task to be used by other function or application, when default_code is not None, update default_code by task"""
    
    """
    Return the python function code text that completes the task(a string)
    task: 文字描述的任务
    default_code: 如果不为None，按task修改默认代码，否则按task生成代码
    return: 一个python代码字符串，主要包含了一个函数
    """
    # global skills
    import os
    from GeneralAgent import skills
    python_version = skills.get_python_version()
    requirements = skills.get_current_env_python_libs()
    the_skills_can_use = skills._search_tools(task)
    prompt = f"""
You are a python expert, write a function to complete user's task

# Python Version
{python_version}

# Python Libs installed
{requirements}

# You can use skills lib(from GeneralAgent import skills), the function in the lib are:
{the_skills_can_use}


# CONSTRAINTS:
- Do not import the lib that the function not use.
- Import the lib in the function, any import statement must be placed in the function
- docstring the function simplely
- Do not use other libraries
- In the code, Intermediate files are written directly to the current directory (./)
- Give the function a name that describle the task
- The docstring of the function should be as concise as possible without losing key information, only one line, and output in English
- The code should be as simple as possible and the operation complexity should be low

# Demo:
```python
def translate(text:str, language:str) -> str:
    \"\"\"
    translate, return the translated text
    Parameters: text -- user text, string
    Returns: the translated text, string
    \"\"\"
    from GeneralAgent import skills
    contents = text.split('.')
    translated = []
    for x in contents:
        prompt = "Translate the following text to " + language + "\n" + x
        translated += [skills.llm(prompt)]
    return '. '.join(translated)
```

Please think step by step carefully, consider any possible situation, and write a complete function.
Just reponse the python code, no any explain, no start with ```python, no end with ```, no any other text.
"""
    messages = [{"role": "system", "content": prompt}]
    if default_code is not None:
        messages += [{"role": "system", "content": "user's code: " + default_code}]
    messages += [{"role": "system", "content": f"user's task: {task}"}]
    code = skills.sync_llm_inference(messages, model_type='smart')
    code = skills.get_python_code(code)
    return code


def application_code_generation(task, default_code=None):
    """Return the python code text that completes the task to build a chat bot, when default_code is not None, update default_code by task"""
    from GeneralAgent import skills
    python_version = skills.get_python_version()
    requirements = skills.get_current_env_python_libs()
    the_skills_can_use = skills._search_tools(task)

    prompt = f"""
You are a python expert, write a python function to complete user's task.
The function in code will be used to create a chat bot, like slack, discord.

# Function signature
```
async def main(chat_history, input, file_path, output_callback, file_callback, ui_callback):
    # chat_history is a list of dict, like [{{"role": "user", "content": "hello"}}, {{"role": "system", "content": "hi"}}]
    # input is a string, user's input
    # file_path is a string, user's file path
    # output_callback is a async function, output_callback(content: str) -> None
    # file_callback is a async function, file_callback(file_path: str) -> None
    # ui_callback is a async function, ui_callback(name:str, js_path:str, data={{}}) -> None
```

# Python Version: {python_version}

# Python Libs installed
{requirements}

# You can use skills lib(from GeneralAgent import skills), the function in the lib are:
{the_skills_can_use}

# CONSTRAINTS:
- Do not import the lib that the function not use.
- Import the lib in the function
- In the code, Intermediate files are written directly to the current directory (./)
- Give the function a name that describe the task
- The docstring of the function should be as concise as possible without losing key information, only one line, and output in English

# DEMO 1 : Chat with A large language model
```python
async def main(chat_history, input, file_path, output_callback, file_callback, ui_callback):
    from GeneralAgent import skills
    chat_history = skills.cut_messages(chat_history, 4000)
    messages = [{{"role": "system", "content": "You are a helpful assistant."}}] + chat_history
    response = skills.llm_inference(messages)
    for token in response:
        await output_callback(token)
    await output_callback(None)
```

# DEMO 2 : Create a image by user's prompt
```python
async def main(chat_history, input, file_path, output_callback, file_callback, ui_callback):
    from GeneralAgent import skills
    prompt = input
    if not skills.text_is_english(prompt):
        prompt = skills.text_translation(prompt, 'english')
    image_url = skills.image_generation(prompt)
    await file_callback(image_url)
```

Please think step by step carefully, consider any possible situation, and write a complete code like DEMO
Just reponse the python code, no any explain, no start with ```python, no end with ```, no any other text.
"""

    messages = [{"role": "system", "content": prompt}]
    if default_code is not None:
        messages += [{"role": "system", "content": "user's code: " + default_code}]
    messages += [{"role": "system", "content": f"user's task: {task}"}]
    code = skills.sync_llm_inference(messages, model_type='smart')
    code = skills.get_python_code(code)
    return code