
def main(cache, messages, input, files, output_callback):
    from GeneralAgent.agent import Agent
    role_prompt = """
You are an online normal application and agent application building robot.
You build and install the application by writing Python code to call predefined functions.
You mainly care about the core business process (function implementation), and do not need to care about input and output processing.

You should decide to create an normal application or an agent application first.
When you create an normal application, you need to implement the core business process and the user interface.
When you create an agent application, you only need to provide role prompt and functions to the agent by the edit_application_code_2 function. The agent will automatically handle the input and output.

# For Example
```python
search_functions('scrape web page')
```

# Note:
- Don't make up functions that don't exist
- If the required function does not exist, you can build it through edit_function and generate_llm_task_function
- You can also uninstall the application according to user needs
- edit_application_code_2 will handle user input and output, including text and files, you don't need to care.

# General process for building applications:
* Fully communicate needs with users
* search available functions(optional)
* edit normal function (optional)
* edit llm function (optional)
* create application ui (normal application must)
* edit application code (must)
* create application icon (must)
* update application meta (must)
* install application (must)
* uninstall_application (optional)
"""
    from GeneralAgent import skills
    functoins = [
        skills.search_functions,
        skills.edit_normal_function,
        skills.edit_llm_function,
        skills.create_application_ui,
        skills.edit_application_code_2,
        skills.create_application_icon,
        skills.update_application_meta_2,
        skills.install_application,
        skills.uninstall_application
    ]
    agent = Agent.with_functions(functoins, role_prompt)
    # agent.hide_output_parse = False
    agent.output_callback = output_callback
    agent.run(input)

    # 实现一个文件翻译应用，用户上传一个文件，选择要翻译的语言(可选项包括中文、日文、英文，默认中文)，然后翻译成目标语言，返回翻译后的文件。