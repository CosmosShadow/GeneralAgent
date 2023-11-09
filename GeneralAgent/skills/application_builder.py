
CODE_DIR = './code'

def get_code_dir():
    global CODE_DIR
    import os
    if not os.path.exists(CODE_DIR):
        os.makedirs(CODE_DIR)
    return CODE_DIR

def set_code_dir(code_dir):
    global CODE_DIR
    CODE_DIR = code_dir

def create_function(func_name:str, task_description:str):
    """
    create a function by task description. Where task_description can include functions in GeneralAgent.skills
    """
    # from GeneralAgent import skills
    import os
    code = function_code_generation(task_description)
    file_path = os.path.join(get_code_dir(), func_name + '.py')
    with open(file_path, 'w') as f:
        f.write(code)

def delete_function(func_name:str) -> None:
    """
    Delete a function by name
    """
    import os
    file_path = os.path.join(get_code_dir(), func_name + '.py')
    if os.path.exists(file_path):
        os.remove(file_path)

def list_functions() -> [str]:
    """
    list all function names
    """
    # TODO function description
    import os
    files = os.listdir(get_code_dir())
    functions = [x.split('.')[0] for x in files]
    return functions

def search_functions(task_description:str) -> str:
    """
    print function signatures that may help to solve the task, and return the function signatures
    """
    from GeneralAgent import skills
    from jinja2 import Template
    functions = skills._search_functions(task_description)
    # print(functions)
    prompt_template = """
# Functions
{{functions}}

# Task
{{task}}

Please return the function signatures that can solve the task.

"""
    prompt = Template(prompt_template).render(task=task_description, functions=functions)
    functions = skills.llm_inference([{'role': 'system', 'content': 'You are a helpful assistant'}, {'role': 'user', 'content': prompt}])
    print(functions)
    return functions

def show_function(func_name:str) -> str:
    """
    Show a function code by name
    """
    import os
    file_path = os.path.join(get_code_dir(), func_name + '.py')
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            code = f.read()
        return code
    else:
        return None

def update_function(func_name:str, task:str):
    """
    update function named func_name code by task
    """
    import os
    file_path = os.path.join(get_code_dir(), func_name + '.py')
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            code = f.read()
        code = function_code_generation(task, default_code=code)
        with open(file_path, 'w') as f:
            f.write(code)
    else:
        create_function(func_name, task)

def edit_function(func_name:str, task_description:str) -> None:
    """
    Edit function code by task_description. task description should be a string and include the detail of task, and what function can be used.
    """
    return update_function(func_name, task_description)

def create_application_icon(application_description:str) -> None:
    """
    Create a application icon by application description. The application description is application_description
    """
    from GeneralAgent import skills
    prompt = skills.ai_draw_prompt_gen("Create an application icon. The application's description is below: \n" + application_description)
    image_url = skills.image_generation(prompt)
    file_path = skills.try_download_file(image_url)
    import os
    target_path = os.path.join(get_code_dir(), 'icon.jpg')
    os.system(f"mv {file_path} {target_path}")


def create_application(task_description:str) -> None:
    """
    Create a application by task_description description. The application name is application_name, the task_description is task_description(string)
    """
    import os
    from GeneralAgent import skills
    # code = application_code_generation(task_description)
    code = generate_agent_code(task_description)
    code_path = os.path.join(get_code_dir(),  'main.py')
    with open(code_path, 'w') as f:
        f.write(code)

def update_application(task_description:str) -> None:
    """
    Update application code by task_description
    """
    import os
    code_path = os.path.join(get_code_dir(),  'main.py')
    old_code = None
    if os.path.exists(code_path):
        with open(code_path, 'r') as f:
            old_code = f.read()
    from GeneralAgent import skills
    code = generate_agent_code(task_description, default_code=old_code)
    # code = application_code_generation(task_description, default_code=old_code)
    with open(code_path, 'w') as f:
        f.write(code)

def edit_application_code(task_description:str) -> None:
    """
    Edit agent code by task_description. task description should be a string and include the detail of task, and what functions can be used. 
    The code for handle user's input and output is already exist, you just need to write the core code to complete the task.
    task_description example: "use skills.image_generation(prompt) generate a image with prompt (in english), return a image url\nskills.translate_text(xxx) to create a image creation Agent"
    """
    return update_application(task_description)


def delete_application():
    """
    Delete application code
    """
    import os
    code_path = os.path.join(get_code_dir(),  'main.py')
    if os.path.exists(code_path):
        os.remove(code_path)

def update_application_meta(application_id:str=None, application_name:str=None, description:str=None, upload_file:str=None) -> None:
    """
    Update application meta data
    application_id: application id, You should name it, example: translat_text, ai_draw
    application_name: application name
    description: application description
    upload_file: 'yes' or 'no', when upload_file is 'yes', the application can upload file, when upload_file is 'no', the application can not upload file
    """
    import os, json
    bot_json_path = os.path.join(get_code_dir(), 'bot.json')
    if os.path.exists(bot_json_path):
        with open(bot_json_path, 'r') as f:
            app_json = json.loads(f.read())
    else:
        app_json = {}
    if application_id is not None:
        from GeneralAgent import skills
        bots = skills.load_applications()
        if application_id in [x['id'] for x in bots]:
            print(f'application_id ({application_id}) exists. ignore If you are just edit the exist application, or you should change the application_id')
        app_json['id'] = application_id
    if application_name is not None:
        app_json['name'] = application_name
    if description is not None:
        app_json['description'] = description
    if upload_file is not None:
        app_json['upload_file'] = upload_file
    # 检查icon是否存在
    if os.path.exists(os.path.join(get_code_dir(), 'icon.jpg')):
        app_json['icon'] = 'icon.jpg'
    with open(bot_json_path, 'w') as f:
        f.write(json.dumps(app_json, indent=4))


def install_application() -> None:
    """
    Install application to chat bot
    """
    # TODO: check function_id and application_name
    import os, json
    bot_json_path = os.path.join(get_code_dir(), 'bot.json')
    if os.path.exists(bot_json_path):
        with open(bot_json_path, 'r') as f:
            app_json = json.loads(f.read())
    else:
        print('applicatoin meta not exists')
        return
    application_id = app_json['id']
    # move code to bot
    target_dir = os.path.join(os.path.dirname(__file__), f'../../webui/server/server/applications/{application_id}/')
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    # print(target_dir)
    os.system(f"mv {get_code_dir()}/* {target_dir}")


def get_existed_application_ids() -> [str]:
    """
    Return all existed application ids
    """
    from GeneralAgent import skills
    bots = skills.load_applications()
    ids = [x['id'] for x in bots]
    return ids


def function_code_generation(task:str, default_code=None):
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
    the_skills_can_use = skills._search_functions(task)
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
        translated += [skills.llm_inference([{'role': 'system', 'content': prompt}])
    return '. '.join(translated)
```

Please think step by step carefully, consider any possible situation, and write a complete function.
Just reponse the python code, no any explain, no start with ```python, no end with ```, no any other text.
"""
    messages = [{"role": "system", "content": prompt}]
    if default_code is not None:
        messages += [{"role": "system", "content": "user's code: " + default_code}]
    messages += [{"role": "system", "content": f"user's task: {task}"}]
    code = skills.llm_inference(messages, model_type='smart')
    code = skills.get_python_code(code)
    return code


def application_code_generation(task, default_code=None):
    """Return the python code text that completes the task to build a chat bot, when default_code is not None, update default_code by task"""
    from GeneralAgent import skills
    python_version = skills.get_python_version()
    requirements = skills.get_current_env_python_libs()
    the_skills_can_use = skills._search_functions(task)

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
    response = skills.llm_inference(messages, stream=True)
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
    code = skills.llm_inference(messages, model_type='smart')
    code = skills.get_python_code(code)
    return code


def generate_agent_code(task_description, default_code=None):
    """Return the python code text that completes the task to build a chat bot, when default_code is not None, update default_code by task"""
    from GeneralAgent import skills
    python_version = skills.get_python_version()
    requirements = skills.get_current_env_python_libs()
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

# CONSTRAINTS:
- Do not import the lib that the function not use.
- Import the lib in the function
- In the code, Intermediate files are written directly to the current directory (./)
- Give the function a name that describe the task
- The docstring of the function should be as concise as possible without losing key information, only one line, and output in English

# DEMO 1 : Application with A large language model
```python
async def main(chat_history, input, file_path, output_callback, file_callback, ui_callback):
    from GeneralAgent import skills
    chat_history = skills.cut_messages(chat_history, 4000)
    messages = [{{"role": "system", "content": "You are a helpful assistant."}}] + chat_history
    response = skills.llm_inference(messages, stream=True)
    for token in response:
        await output_callback(token)
    await output_callback(None)
```

# DEMO 2 : Agent with functions
```python
async def main(chat_history, input, file_path, output_callback, file_callback, ui_callback):
    from GeneralAgent.agent import Agent
    role_prompt = \"\"\"
你是一个翻译助手。
你通过编写python代码调用 # Run python 中预定义好的函数，来完成用户需求。
\"\"\"
    functions = [
        skills.text_translation
    ]
    agent = Agent.agent_with_functions(functions, role_prompt)
    await agent.run(input, output_callback=output_callback)
```python

# There are two function types:
1. Application: like DEMO1, The application process is fixed and less flexible, but the function will be more stable
2. Agent: like DEMO2, Agent is a chat bot that can use functions to complete user's task. The agent will automatic handle user's input and output
You can choose one of them to complete the task.

Please think step by step carefully, consider any possible situation, and write a complete code like DEMO
Just reponse the python code, no any explain, no start with ```python, no end with ```, no any other text.
"""

    messages = [{"role": "system", "content": prompt}]
    if default_code is not None:
        messages += [{"role": "system", "content": "user's code: " + default_code}]
    messages += [{"role": "system", "content": f"user's task: {task_description}"}]
    code = skills.llm_inference(messages, model_type='smart')
    code = skills.get_python_code(code)
    return code