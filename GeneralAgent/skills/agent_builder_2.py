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

# Task
Create a React function component named LibTemplate in tsx language. 
The component should have the following functionality:
{{task}}

# Import
Use the following import syntax:
```
const React = (window as any).React;
const antd = (window as any).antd;
```
No other import methods are allowed.

# DEMO

```tsx
const React = (window as any).React;
const antd = (window as any).antd;

interface Props {
  save_data: (user_data:any)=>void,
  FileUploadConponent: (props: {onUploadSuccess: (file_path: string) => void, title?: string}) => React.ReactElement
}

const LibTemplate = (props: Props) => {
  // user save_data to save the user_data
  // user_data will be processed into a string through save_data using JSON.stringify({'data': user_data}) and sent to the backend
  // use FileUploadConponent to upload file (<props.FileUploadConponent onUploadSuccess={handleUploadSuccess} title='上传xx'/>) and add file_path to data before save
};

export default LibTemplate;
```

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


def create_application_ui(task: str, ui_dir: str = './ui', component_name: str = None) -> (str, str):
    """
    Convert a given task description into UI components. 
    In the code, user_data will be processed into a string through save_data using JSON.stringify({'data': user_data}) and sent to the backend
    @param task: The task description.
    @param ui_dir: The directory to store the UI library.
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
    if not os.path.exists(ui_dir):
        os.makedirs(ui_dir)
    target_dir = os.path.join(ui_dir, lib_name)
    content = _llm_write_ui_lib(lib_name, task)
    code = skills.extract_tsx_code(content)
    success = skills.compile_tsx(lib_name, code, target_dir)
    if success:
        return lib_name, os.path.join(target_dir, 'index.js'), code
    else:
        return None
    

def update_application_meta_2(
        application_id:str=None,
        type:str=None,
        application_name:str=None,
        description:str=None,
        js_name:str=None,
        js_path:str=None,
        agent_can_upload_file=None,
        ) -> None:
    """
    Update application meta data. When type is application, you should provide js_name and js_path. When type is agent, you should ignore js_name and js_path.
    @param application_id: application id, You should name it, example: translat_text, ai_draw
    @param type: application type, one of ['application', 'agent']. application is a normal application with ui, agent is a agent application with chat interface.
    @param application_name: application name
    @param description: application description
    @param js_name: js file name
    @param js_path: js file path
    @param agent_can_upload_file: agent can upload file or not, default is False, if True, agent can upload file to the application
    @return: None
    """
    import os, json
    from GeneralAgent import skills
    bot_json_path = os.path.join(skills.get_code_dir(), 'bot.json')
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
    if type is not None:
        app_json['type'] = type
    if application_name is not None:
        app_json['name'] = application_name
    if description is not None:
        app_json['description'] = description
    app_json['upload_file'] = 'yes'
    if js_name is not None:
        app_json['js_name'] = js_name
    if js_path is not None:
        app_json['js_path'] = js_path
    if agent_can_upload_file is not None:
        app_json['upload_file'] = 'yes'
    if os.path.exists(os.path.join(skills.get_code_dir(), 'icon.jpg')):
        app_json['icon'] = 'icon.jpg'
    else:
        del app_json['icon']
    with open(bot_json_path, 'w') as f:
        f.write(json.dumps(app_json, indent=4))