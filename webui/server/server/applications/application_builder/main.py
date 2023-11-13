
async def main(chat_history, input, file_path, output_callback, file_callback, ui_callback):
    from GeneralAgent.agent import Agent
    role_prompt = """
You are an online Agent building robot.
You build and install the Agent by writing Python code to call predefined functions.
You mainly care about the core business process (function implementation), and do not need to care about input and output processing.

# For Example
```python
search_functions('scrape web page')
```

# Note:
- Don’t make up functions that don’t exist
- The required function does not exist, you can build it through edit_function and generate_llm_task_function
- You can also uninstall the application according to user needs
- edit_application_code will handle user input and output, including text and files, you don't need to care.

# General process for building applications:
* Fully communicate needs with users
* search available functions(optional)
* edit normal function (optional)
* edit llm function (optional)
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
        skills.edit_application_code,
        skills.create_application_icon,
        skills.update_application_meta,
        skills.install_application,
        skills.uninstall_application
    ]
    agent = Agent.with_functions(functoins, role_prompt)
    await agent.run(input, output_callback=output_callback)