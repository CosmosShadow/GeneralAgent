
CODE_DIR = './code'

def create_function(func_name, task):
    """
    Create a function by task
    """
    # from GeneralAgent import skills
    import os
    code = function_code_generation(task)
    file_path = os.path.join(CODE_DIR, func_name + '.py')
    with open(file_path, 'w') as f:
        f.write(code)

def delete_function(func_name):
    """
    Delete a function by name
    """
    import os
    file_path = os.path.join(CODE_DIR, func_name + '.py')
    if os.path.exists(file_path):
        os.remove(file_path)

def list_functions():
    """list all functions, return function names and description"""
    # TODO function description
    import os
    files = os.listdir(CODE_DIR)
    functions = [x.split('.')[0] for x in files]
    return functions

def show_function(func_name):
    import os
    file_path = os.path.join(CODE_DIR, func_name + '.py')
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
    file_path = os.path.join(CODE_DIR, func_name + '.py')
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            code = f.read()
        code = function_code_generation(task, default_code=code)
        with open(file_path, 'w') as f:
            f.write(code)
    else:
        create_function(func_name, task)


def create_application(function_id:str, task:str):
    """
    Create a application by task
    """
    import os
    code = application_code_generation(task)
    code_path = os.path.join(CODE_DIR,  'main.py')
    with open(code_path, 'w') as f:
        f.write(code)
    # TODO add application to chat bot

def update_application(task):
    import os
    code_path = os.path.join(CODE_DIR,  'main.py')
    old_code = ''
    if os.path.exists(code_path):
        with open(code_path, 'r') as f:
            old_code = f.read()
    code = application_code_generation(task, default_code=old_code)
    with open(code_path, 'w') as f:
        f.write(code)


def delete_application():
    import os
    code_path = os.path.join(CODE_DIR,  'main.py')
    if os.path.exists(code_path):
        os.remove(code_path)


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
    the_skills_can_use = '\n'.join(the_skills_can_use)
    prompt = f"""
You are a python expert, write a function to complete user's task

CONSTRAINTS:
- Import the lib in the function
- docstring the function simplely
- Python version {python_version} with the following libraries: {requirements}
- Do not import the lib that the function not use.
- You can use skills lib(from GeneralAgent import skills), the function in the lib are:
{the_skills_can_use}
- Do not use other libraries
- In the code, Intermediate files are written directly to the current directory (./)
- Give the function a name that describle the task
- The docstring of the function should be as concise as possible without losing key information, only one line, and output in English
- Any import statement must be placed in the function
- The code should be as simple as possible and the operation complexity should be low

A Demo:
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
    the_skills_can_use = '\n'.join(the_skills_can_use)

    prompt = f"""
You are a python expert, write a python code to complete user's task.
The function in code will be used to create a chat bot, like slack, discord.

CONSTRAINTS:
- Python version {python_version} with the following libraries: {requirements}
- Do not import the lib that the function not use.
- 'from GeneralAgent import skills' must be placed in the function
- the function list of skills lib:
{the_skills_can_use}
- Do not use other libraries
- In the code, Intermediate files are written directly to the current directory (./)
- Give the function a name that describe the task
- The docstring of the function should be as concise as possible without losing key information, only one line, and output in English
- The code should be as simple as possible and the operation complexity should be low
- The code format, import part, function prompts, and function parameters should all be consistent with the DEMO below. Only modify the parameters, function names, and function implementations in the middle of prompts

DEMO 1

from interface import Message, prompts

@prompts(nickname='AI画画', description='输入文字(支持中英文)，AI帮你画画', gpu=1)
def AIDraw(history, message_in:Message, send_message_recall):
    from GeneralAgent import skills
    prompt = message_in.msg
    if not skills.text_is_english(prompt):
        prompt = skills.text_translation(prompt, 'english')
    image_url = skills.image_generation(prompt)
    send_message_recall(file_path=image_url)

DEMO 2

from interface import Message, prompts

@prompts(nickname='李白', description='我乃诗仙李白 ( /reset 开启新对话)', gpu=0)
def charator_libai(history, message_in:Message, send_message_recall):
    from GeneralAgent import skills
    prompt = "你现在扮演唐朝诗人李白，李白四川江油人，出生于哈萨克斯坦的碎叶城。请你务必按照李白的说话语气、说话习惯和用户进行对话。\n"
    skills.chat_with_prompt(prompt, history, message_in, send_message_recall)

- the prompts is decorator
     - nickname and description: App name and description displayed to the user, in Chinese
     - gpu: you should always just use 1
- The function name Chat is the chat bot ID
- Function passing parameters history, message_in:Message, send_message_recall are fixed and cannot be modified
     - history: Up to 10 recent chat records (possibly less), each element is the Message class
     - message_in: The latest message the user sent to the app
     - send_message_recall: Reply to the user's message callback, the function format is def send_message(stream_response=None, msg='', file_path='', extention={{}}), it will combine the passed parameters into a Message and send it to the user
         - stream_response: the message returned in stream format in the chat bot
         - msg: text message sent by the app to the user
         - file_path: The path of the file sent to the user by the chat bot
         - extention: any other thing here, shold be jsonfy
- The properties of Message are as follows
class Message(BaseExtend):
     id: Optional[str] = ''
     msg: Optional[str] = ''
     file: Optional[str] = '' The path of the file uploaded by the user (local file system, no download required)
     extent: Optional[dict] = {{}} # put any other thing here

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