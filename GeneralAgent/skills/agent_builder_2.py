def _llm_write_ui_lib(lib_name:str, task:str) -> str:
    """
    Write a UI library for a given task description.
    @param lib_name: The name of the UI library.
    @param task: The task description.
    @return: The UI library code.
    """
    from GeneralAgent import skills
    prompt_template = """
You are a React and Typescript expert.
You are going to create a UI library for a given task description.

# Import
Use the following import syntax:
```
const React = (window as any).React;
const antd = (window as any).antd;
```
No other import methods are allowed.

# Code Template

```tsx
const React = (window as any).React;
const antd = (window as any).antd;

interface Props {
  save_data: (user_data:any)=>void,
  FileUploadConponent: (props: {onUploadSuccess: (file_path: string) => void, title?: string}) => React.ReactElement
}

// user save_data to save the user_data
// user_data will be processed into a string through save_data using JSON.stringify({'data': user_data}) and sent to the backend
// use FileUploadConponent to upload file (<props.FileUploadConponent onUploadSuccess={handleUploadSuccess} title=''/>) and add file_path to data before save

const LibTemplate = (props: Props) => {

  const handleCommit = () => {
    #   props.save_data(all_data_should_save)
  };

  return (<>{xxx}</>);
};

export default LibTemplate;
```

# DEMO
Task: Upload a text file, and to translate the text file to another language, default is Chinese, options are Chinese, Japanese, English.
Reponse:
```tsx
const React = (window as any).React;
const antd = (window as any).antd;

interface Props {
  save_data: (user_data: any) => void,
  FileUploadConponent: (props: { onUploadSuccess: (file_path: string) => void, title?: string }) => React.ReactElement
}

const LibTemplate = (props: Props) => {
  const [filePath, setFilePath] = React.useState("");
  const [targetLanguage, setTargetLanguage] = React.useState("Chinese");

  const handleUploadSuccess = (file_path: string) => {
    setFilePath(file_path);
  };

  const handleCommit = () => {
    const all_data_should_save = {
      filePath,
      targetLanguage
    };
    props.save_data(all_data_should_save);
  };

  const handleLanguageChange = (value: string) => {
    setTargetLanguage(value);
  };

  return (
    <>
      <props.FileUploadConponent onUploadSuccess={handleUploadSuccess} title="Upload File" />
      {filePath && <div>File uploaded: {filePath}</div>}
      <antd.Select defaultValue="Chinese" onChange={handleLanguageChange}>
        <antd.Select.Option value="Chinese">Chinese</antd.Select.Option>
        <antd.Select.Option value="Japanese">Japanese</antd.Select.Option>
        <antd.Select.Option value="English">English</antd.Select.Option>
      </antd.Select>
      <antd.Button type="primary" onClick={handleCommit}>
        Submit
      </antd.Button>
    </>
  );
};

export default LibTemplate;
```

# CONSTRAINTS:
- Create a React function component named LibTemplate in tsx language. 
- The component only save data to backend, no need to display data, or result of task.
- When uploaded file, should show the file path
- No need to ask user set result file name, backend server will use a unique name to save the file.

# Task

{{task}}

Please reponse the component code which finish the task without any explaination.
"""

    from jinja2 import Template
    prompt = Template(prompt_template).render(task=task)
    messages = [{'role': 'system', 'content': prompt}]
    response = skills.llm_inference(messages, model_type="normal", stream=True)
    result = ''
    for token in response:
        result += token
    result = result.replace('LibTemplate', lib_name)
    return result


def create_application_ui(task: str, component_name: str = None) -> (str, str, str):
    """
    Convert a given task description into UI components. 
    In the code, user_data will be processed into a string through save_data using JSON.stringify({'data': user_data}) and sent to the backend
    @param task: Task description, should include all details related to creating the UI
    @param component_name: The name of the UI library.
    @return: The name of the UI library,  the path of the UI library, the code of the UI library. None if failed. 
    Example:
        create_application_ui('A task description with all the necessary details')
    """
    import os
    import uuid
    from GeneralAgent import skills
    lib_name = component_name
    if lib_name is None:
        lib_name = 'Lib' + str(uuid.uuid1())[:4]
    target_dir = os.path.join(skills.get_code_dir(), lib_name)
    content = _llm_write_ui_lib(lib_name, task)
    code = skills.extract_tsx_code(content)
    success = skills.compile_tsx(lib_name, code, target_dir)
    if success:
        js_path = os.path.join(lib_name, 'index.js')
        print(f'UI library created successfully.\n js_component_name: {lib_name}\n js_path: {js_path}\n code: \n```tsx\n{code}\n```')
        return lib_name, js_path, code
    else:
        return None
    

def update_application_meta_2(
        application_id:str=None,
        type:str=None,
        application_name:str=None,
        description:str=None,
        js_component_name:str=None,
        js_path:str=None,
        agent_can_upload_file=None,
        ) -> None:
    """
    Update application meta data. When type is application, you should provide js_component_name and js_path. When type is agent, you should ignore js_component_name and js_path.
    @param application_id: application id, You should name it, example: translat_text, ai_draw
    @param type: application type, one of ['application', 'agent']. application is a normal application with ui, agent is a agent application with chat interface.
    @param application_name: application name
    @param description: application description
    @param js_component_name: js component name
    @param js_path: js file path
    @param agent_can_upload_file: agent can upload file or not, default is False, if True, agent can upload file to the application
    @return: None
    """
    import os, json
    from GeneralAgent import skills
    bot_json_path = os.path.join(skills.get_code_dir(), 'bot.json')
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
    if type is not None:
        app_json['type'] = type
    if application_name is not None:
        app_json['name'] = application_name
    if description is not None:
        app_json['description'] = description
    app_json['upload_file'] = 'yes'
    if js_component_name is not None:
        app_json['js_name'] = js_component_name
    if js_path is not None:
        app_json['js_path'] = js_path
    if agent_can_upload_file is not None:
        app_json['upload_file'] = 'yes'
    if os.path.exists(os.path.join(skills.get_code_dir(), 'icon.jpg')):
        app_json['icon'] = 'icon.jpg'
    else:
        del app_json['icon']
    with open(bot_json_path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(app_json, indent=4))


def edit_application_code_2(task_description:str) -> str:
    """
    edit_application_code_2 is an Agent. You just tell it what will be done and vailable functions, it will generate a python function to complete the task. the code will be saved in main.py, which will be used to create a normal application or agent application.
    @param task_description: task description, should be a string and include the detail of task, and what functions can be used. when building a normal application, task_desciption should have the detail of data format that ui save to backend, example: "Create a image creation application. Available functions:\n\nskills.create_image(prompt) generate a image with prompt (in english), return a image url\n\nskills.translate_text(content, target_language), data format is {'data': {'prompt': 'xxxxx'}}". when building a agent application, ignore the detail of data format, example: "Create a agent. role prompt is : You are a image creator, transfer users's need to create a image.  Available functions:\n\n xxxx"
    @return: python code for the task
    """
    import os
    from GeneralAgent import skills
    code_path = os.path.join(skills.get_code_dir(),  'main.py')
    old_code = None
    if os.path.exists(code_path):
        with open(code_path, 'r', encoding='utf-8') as f:
            old_code = f.read()
    code = _generate_agent_code(task_description, default_code=old_code)
    with open(code_path, 'w', encoding='utf-8') as f:
        f.write(code)
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
def main(cache, messages, input, files, output_callback):
    chat bot entry function, return the chat bot object, you can use it to store any data, and use it in next run
    @param cache: the return value of last run, you can use it to store any data, and use it in next run
    @param messages: chat messages, list of dict, like [{{'role': 'system', 'content': 'You are a helpful assistant.'}}, {{'role': 'user', 'content': '1 + 1 = ?'}}]
    @param input: user chat input for agent application. Or json string for normal application, include user's input and upload files, like '{{"data": {{"input": "1 + 1 = ?", "files": ["a.txt", "b.txt"]}}}}'
    @param files: user upload files, list of file path, like ['a.txt', 'b.txt']. the parameter is only for agent application, you can ignore it when building a normal application
    @param output_callback: output callback function, like output_callback('2'). you can pass None to output_callback to start a new chat session.
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

# DEMO 1 : normal application, write user's input to a file and return
```python
def main(cache, messages, input, files, output_callback):
    from GeneralAgent import skills
    import json
    data = json.loads(input)['data']
    # file_path should be a unique name, because the file will not be deleted, and the application will run many times.
    file_path = skills.unique_name() + '.json
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(data))
    output_callback(f'file saved: [user_data.json](sandbox:{{file_path}})')
```

# DEMO 2 : agent application, Agent with functions
```python
def main(cache, messages, input, files, output_callback):
    from GeneralAgent.agent import Agent
    role_prompt = \"\"\"
You are a translation agent.
You complete user requirements by writing python code to call the predefined functions.
\"\"\"
    functions = [
        skills.translate_text
    ]
    agent = cache
    if agent is None:
        agent = Agent.with_functions(functions)
        agent.add_role_prompt(role_prompt)
        agent.output_callback = output_callback
    agent.run(input)
    return agent
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