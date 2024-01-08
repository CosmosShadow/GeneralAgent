
CODE_DIR = './code'

def get_code_dir():
    global CODE_DIR
    import os
    if not os.path.exists(CODE_DIR):
        os.makedirs(CODE_DIR)
    return CODE_DIR

def _set_code_dir(code_dir):
    global CODE_DIR
    CODE_DIR = code_dir


def search_functions(function_description:str) -> str:
    """
    search function by description and return the function signatures
    @param function_description (str): the function description.
    @return: The generated Python function signatures as a string.
    """
    from GeneralAgent import skills
    functions = skills._search_functions(function_description)
    print(functions)
    return functions
    from jinja2 import Template
#     # print(functions)
#     prompt_template = """
# # Functions
# {{functions}}

# # Task
# {{task}}

# Please return the function signatures that can solve the task.

# """
#     prompt = Template(prompt_template).render(task=task_description, functions=functions)
#     functions = skills.llm_inference([{'role': 'system', 'content': 'You are a helpful assistant'}, {'role': 'user', 'content': prompt}])
#     print(functions)
#     return functions


def edit_normal_function(function_name:str, task_description:str) -> None:
    """
    Edit normal function code by task_description
    @param function_name: The name of the function to be generated.
    @param task_description (str): A description of the task that the generated function should perform and what functions can be used.
    @return: The generated Python function signature as a string.
    """
    return _edit_function(function_name, task_description, _generate_function_code)


def edit_llm_function(function_name: str, task_description:str) -> str:
    """
    This function generates a Python function to perform a specific task using a large language model (LLM), such as translation, planning, answering general knowledge questions and so on.
    @param function_name: The name of the function to be generated.
    @param task_description (str): A description of the task that the generated function should perform.
    @return: The generated Python function signature as a string.
    """
    return _edit_function(function_name, task_description, _generate_llm_task_function)


def _edit_function(function_name: str, task_description:str, code_fun) -> str:
    import os
    from GeneralAgent import skills
    from GeneralAgent.utils import get_functions_dir
    file_path = os.path.join(get_functions_dir(), function_name + '.py')
    code = None
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
    task_description += f'\n# Function name: {function_name}'
    code = code_fun(task_description, default_code=code)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(code)
    funcs, error = skills.load_functions_with_path(file_path)
    funcs = [x for x in funcs if x.__name__ == function_name]
    if len(funcs) <= 0:
        print(error)
        return error
    else:
        signature = skills.get_function_signature(funcs[0], 'skills')
        skills._load_remote_funs()
        print(signature)
        return signature

def delete_function(func_name:str) -> None:
    """
    Delete a function by name
    """
    import os
    from GeneralAgent.utils import get_functions_dir
    file_path = os.path.join(get_functions_dir(), func_name + '.py')
    if os.path.exists(file_path):
        os.remove(file_path)

def create_application_icon(application_description:str) -> None:
    """
    Create a application icon by application description. The application description is application_description
    """
    import os
    from GeneralAgent import skills
    prompt = skills.ai_draw_prompt_gen("Create an application icon. The application's description is below: \n" + application_description)
    image_url = skills.create_image(prompt)
    file_path = skills.try_download_file(image_url)
    target_path = os.path.join(get_code_dir(), 'icon.jpg')
    os.system(f"mv {file_path} {target_path}")
    

def edit_application_code(task_description:str) -> None:
    """
    edit_application_code is an Agent. You just tell it what will be done and vailable functions, it will generate a python function to complete the task.
    Edit agent code by task_description. task description should be a string and include the detail of task, and what functions can be used. 
    task_description example: "Create a image creation agent. Available functions:\n\nskills.create_image(prompt) generate a image with prompt (in english), return a image url\n\nskills.translate_text(content, target_language)"
    """
    import os
    code_path = os.path.join(get_code_dir(),  'main.py')
    old_code = None
    if os.path.exists(code_path):
        with open(code_path, 'r', encoding='utf-8') as f:
            old_code = f.read()
    from GeneralAgent import skills
    code = _generate_agent_code(task_description, default_code=old_code)
    with open(code_path, 'w', encoding='utf-8') as f:
        f.write(code)


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
        with open(bot_json_path, 'r', encoding='utf-8') as f:
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
    if os.path.exists(os.path.join(get_code_dir(), 'icon.jpg')):
        app_json['icon'] = 'icon.jpg'
    else:
        del app_json['icon']
    with open(bot_json_path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(app_json, indent=4))


def install_application() -> None:
    """
    Install application to chat bot
    """
    # TODO: check function_id and application_name
    import os, json
    bot_json_path = os.path.join(get_code_dir(), 'bot.json')
    if os.path.exists(bot_json_path):
        with open(bot_json_path, 'r', encoding='utf-8') as f:
            app_json = json.loads(f.read())
    else:
        print('applicatoin meta not exists')
        return
    application_id = app_json['id']
    # move code to bot
    from GeneralAgent.utils import get_applications_dir
    target_dir = os.path.join(get_applications_dir(), application_id)
    if os.path.exists(target_dir):
        import shutil
        shutil.rmtree(target_dir)
    os.makedirs(target_dir)
    # print(target_dir)
    os.system(f"cp -r {get_code_dir()}/* {target_dir}")


def uninstall_application() -> None:
    """
    Uninstall application from chat bot
    """
    import os, json
    bot_json_path = os.path.join(get_code_dir(), 'bot.json')
    if os.path.exists(bot_json_path):
        with open(bot_json_path, 'r', encoding='utf-8') as f:
            app_json = json.loads(f.read())
    else:
        print('applicatoin meta not exists')
        return
    application_id = app_json['id']
    # move code to bot
    from GeneralAgent.utils import get_applications_dir
    target_dir = os.path.join(get_applications_dir(), application_id)
    if os.path.exists(target_dir):
        import shutil
        shutil.rmtree(target_dir)



def _generate_function_code(task:str, default_code=None, search_functions=False):
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
    the_skills_can_use = skills._search_functions(task) if search_functions else ''
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
        translated += [skills.llm_inference([{{'role': 'system', 'content': prompt}}])
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
def main(chat_history, input, file_path, output_callback, file_callback, ui_callback):
    # chat_history is a list of dict, like [{{"role": "user", "content": "hello"}}, {{"role": "system", "content": "hi"}}]
    # input is a string, user's input
    # file_path is a string, user's file path
    # output_callback is a function, output_callback(content: str) -> None
    # file_callback is a function, file_callback(file_path: str) -> None
    # ui_callback is a function, ui_callback(name:str, js_path:str, data={{}}) -> None
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
def main(chat_history, input, file_path, output_callback, file_callback, ui_callback):
    from GeneralAgent import skills
    chat_history = skills.cut_messages(chat_history, 4000)
    messages = [{{"role": "system", "content": "You are a helpful assistant."}}] + chat_history
    response = skills.llm_inference(messages, stream=True)
    for token in response:
        output_callback(token)
    output_callback(None)
```

# DEMO 2 : Create a image by user's prompt
```python
def main(chat_history, input, file_path, output_callback, file_callback, ui_callback):
    from GeneralAgent import skills
    prompt = input
    if not skills.text_is_english(prompt):
        prompt = skills.translate_text(prompt, 'english')
    image_url = skills.create_image(prompt)
    file_callback(image_url)
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


def _generate_agent_code(task_description, default_code=None):
    """Return the python code text that completes the task to build a chat bot, when default_code is not None, update default_code by task"""
    from GeneralAgent import skills
    python_version = skills.get_python_version()
    requirements = skills.get_current_env_python_libs()
    prompt = f"""
You are a python expert, write a python function to complete user's task.
The function in code will be used to create a chat bot, like slack, discord.

# Function signature
```
def main(chat_history, input, file_path, output_callback, file_callback, ui_callback):
    # chat_history is a list of dict, like [{{"role": "user", "content": "hello"}}, {{"role": "system", "content": "hi"}}]
    # input is a string, user's input
    # file_path is a string, user's file path
    # output_callback is a function, output_callback(content: str) -> None
    # file_callback is a function, file_callback(file_path: str) -> None
    # ui_callback is a function, ui_callback(name:str, js_path:str, data={{}}) -> None
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
- Every created file should have a unique name, which can be generated by skills.unique_name()

# DEMO 1 : write user's input to a file and return
```python
def main(chat_history, input, file_path, output_callback, file_callback, ui_callback):
    from GeneralAgent import skills
    
```

# DEMO 2 : Agent with functions
```python
def main(chat_history, input, file_path, output_callback, file_callback, ui_callback):
    from GeneralAgent.agent import Agent
    role_prompt = \"\"\"
You are a translation agent.
You complete user requirements by writing python code to call the predefined functions.
\"\"\"
    functions = [
        skills.translate_text
    ]
    agent = Agent.with_functions(functions, role_prompt)
    agent.run(input, stream_callback=output_callback)
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


def _generate_llm_task_function(task_description, default_code=None):
    """
    This function generates a Python function to perform a specific task using a large language model (LLM), such as translation, planning, answering general knowledge questions.
    
    Parameters:
    task_description (str): A description of the task that the generated function should perform.

    Returns:
    str: The generated Python function code as a string.
    """
    import os
    from GeneralAgent import skills
    python_version = skills.get_python_version()
    requirements = skills.get_current_env_python_libs()
    the_skills_can_use = skills._search_functions(task_description) if search_functions else ''
    prompt = f"""
You are a python expert, write a function to complete user's task

# Python Version
{python_version}

# Python Libs installed
{requirements}

# You can use skills lib(from GeneralAgent import skills), the function in the lib are:

def skills.llm_inference_to_json(messages, json_schema):
     Run LLM (large language model) inference on the provided messages, The total number of tokens in the messages and the returned string must be less than 8000.
     @param messages: Input messages for the model, like [{{'role': 'system', 'content': 'You are a helpful assistant'}}, {{'role': 'user', 'content': 'translate blow to english:\nxxxx'}}]
     @param json_schema: the json schema of return dictionary, like {{"type": "object", "properties": {{"name": {{"type": "string"}}, "age": {{"type": "integer" }} }} }}
     @return returned as a dictionary According to the provided JSON schema.

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
- Every created file should have a unique name, which can be generated by skills.unique_name()

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
        translated += [skills.llm_inference([{{'role': 'system', 'content': prompt}}])
    return '. '.join(translated)
```

Please think step by step carefully, consider any possible situation, and write a complete function.
Just reponse the python code, no any explain, no start with ```python, no end with ```, no any other text.
"""
    messages = [{"role": "system", "content": prompt}]
    if default_code is not None:
        messages += [{"role": "system", "content": "user's code: " + default_code}]
    messages += [{"role": "system", "content": f"user's task: {task_description}"}]
    code = skills.llm_inference(messages, model_type='smart')
    code = skills.get_python_code(code)
    return code

#     from GeneralAgent import skills
#     from jinja2 import Template
#     prompt_template = """
# 你是一个python专家。


# Your job is to have a large language model (LLM) perform specific tasks, such as translation, planning, answering general knowledge questions, etc.
# Your job is to have a large language model (LLM) perform specific tasks, such as translation, planning, answering general knowledge questions, etc.
# Large language model calling function:

# ```python
# def xxx(xxx):
#      \"\"\"
#      xxx
#      \"\"\"
#      from GeneralAgent import skills
#      # skills.llm_inference_to_json
# ```

# # Task

# {{task}}

# # Note:

# - All imports should be placed inside the function.
# - While creating your function, consider the all edge cases.
# - Do not use any other libraries except llm_inference_to_json and installed libraries.
# - The llm_inference_to_json function requires that the input messages are less than 8000, and the output length is less than 8000. - 
# - When the task cannot be completed through one llm_inference_to_json, you should consider task disassembly.
# """
#     prompt = Template(prompt_template).render({'task': task_description})
#     if default_code is not None:
#         prompt += '\n' + 'user\'s code: ' + default_code + '\nUpdate the code to complete the task'
#     result = skills.llm_inference([{'role': 'system', 'content': prompt}, {'role': 'user', 'content': 'You are a python expert.'}, {'role': 'user', 'content': prompt}], model_type="smart")
#     code = skills.get_python_code(result)
#     return code


# def create_function(func_name:str, task_description:str):
#     """
#     create a function by task description. Where task_description can include functions in GeneralAgent.skills
#     """
#     # from GeneralAgent import skills
#     import os
#     code = _generate_function_code(task_description)
#     file_path = os.path.join(get_code_dir(), func_name + '.py')
#     with open(file_path, 'w', encoding='utf-8') as f:
#         f.write(code)

# def delete_function(func_name:str) -> None:
#     """
#     Delete a function by name
#     """
#     import os
#     file_path = os.path.join(get_code_dir(), func_name + '.py')
#     if os.path.exists(file_path):
#         os.remove(file_path)

# def list_functions() -> [str]:
#     """
#     list all function names
#     """
#     # TODO function description
#     import os
#     files = os.listdir(get_code_dir())
#     functions = [x.split('.')[0] for x in files]
#     return functions

# def show_function(func_name:str) -> str:
#     """
#     Show a function code by name
#     """
#     import os
#     file_path = os.path.join(get_code_dir(), func_name + '.py')
#     if os.path.exists(file_path):
#         with open(file_path, 'r', encoding='utf-8') as f:
#             code = f.read()
#         return code
#     else:
#         return None


# def create_application(task_description:str) -> None:
#     """
#     Create a application by task_description description. The application name is application_name, the task_description is task_description(string)
#     """
#     import os
#     from GeneralAgent import skills
#     # code = application_code_generation(task_description)
#     code = _generate_agent_code(task_description)
#     code_path = os.path.join(get_code_dir(),  'main.py')
#     with open(code_path, 'w', encoding='utf-8') as f:
#         f.write(code)