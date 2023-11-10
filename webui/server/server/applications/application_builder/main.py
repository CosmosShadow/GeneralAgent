
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
- edit_application_code will handle user input and output, including text and files, you don't need to care.
- Do not use functions that have not appeared before, otherwise an error will be reported.
- The search found that there are not enough functions, you need to implement them through edit_function and generate_llm_task_function.
- You can also uninstall the application according to user needs

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

    skill_names = [
        'search_functions',
        'edit_function',
        'edit_normal_function',
        'edit_llm_function',
        'edit_application_code',
        'create_application_icon',
        'update_application_meta',
        'install_application',
        "uninstall_application"
    ]
    agent = Agent.agent_with_skills(skill_names, role_prompt)
    await agent.run(input, output_callback=output_callback)