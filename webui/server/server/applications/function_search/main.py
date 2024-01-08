def main(cache, messages, input, files, output_callback):
    """
    @param cache: cache object
    @param messages: chat messages, list of dict, like [{'role': 'system', 'content': 'You are a helpful assistant.'}, {'role': 'user', 'content': '1 + 1 = ?'}]
    @param input: user input, str
    @param files: user upload files, list of file path, like ['a.txt', 'b.txt']
    @param output_callback: output callback function, like output_callback('2'). you can pass None to output_callback to start a new chat session.
    """
    from GeneralAgent.agent import Agent
    from GeneralAgent import skills
    from GeneralAgent import FunctionSearcher

    role_prompt_append = """
# Search for functions
- use `_search_function` to search for available functions, and then execute the functions to complete user needs.
## DEMO: draw a image about Beijing
```python
search_functions('draw image')
```
Result: "tools.create_image(prompt) -> str: draw image given a prompt, returns the image path. Note: limit to generate violent, adult, or hateful content"
Then Draw a image
```python
image_path = tools.create_image('image description')
image_path
```
"""

    def get_weather(city:str) -> str:
        return 'Sunny'

    tools = FunctionSearcher('tools')
    tools._add_functions([get_weather, skills.create_image])
    
    agent = Agent.with_functions([tools._search_function], workspace='./', variables={'tools': tools})
    agent.add_role_prompt(role_prompt_append)
    agent.run(input, stream_callback=output_callback)