# GeneralAgent: From LLM to Agent

<p align="center">
<a href="README_CN.md"><img src="https://img.shields.io/badge/文档-中文版-blue.svg" alt="CN doc"></a>
<a href="README.md"><img src="https://img.shields.io/badge/document-English-blue.svg" alt="EN doc"></a>
</p>

GeneralAgent is a Python-native Agent framework that aims to seamlessly integrate large language models with Python.

**Main features**

* **Tool call**: GeneralAgent does not rely on the function call of large models, but calls tools through the python code interpreter.

* **Serialization**: GeneralAgent supports serialization, including memory and python execution status, and is ready to use

* **Self-call**: GeneralAgent minimizes the number of calls to large models through self-call and stack memory to efficiently handle complex tasks. For more details, please see our [paper](./docs/paper/General_Agent__Self_Call_And_Stack_Memory.pdf)

* **Deployment service**: Use [AgentServer (to be open source)](https://github.com/CosmosShadow/AgentServer) to deploy Agents and quickly provide services to large-scale users.

With GeneralAgent, you can:

* Quickly configure role, functions, and knowledge bases to create Agent.

* Execute stable and complex business processes and coordinate multiple Agents to complete tasks.
* Use the `agent.run` function to execute commands and produce structured output, beyond simple text responses.
* Use the `agent.user_input` function to dynamically interact with the user.



## Installation

```bash
pip install GeneralAgent
```



## Configuration

Refer to the [.env.example](./.env.example) file to configure the key or other parameters of the large model

```bash
export OPENAI_API_KEY=your_openai_api_key
```

Or configure in the code

```python
from GeneralAgent import Agent
agent = Agent('You are a helpful agent.', api_key='sk-xxx')
```



## Usage

### Quick Start

```python
from GeneralAgent import Agent

# Streaming output of intermediate results
def output_callback(token):
    token = token or '\n'
    print(token, end='', flush=True)

agent = Agent('You are an AI assistant, reply in Chinese.', output_callback=output_callback)
while True:
    query = input('Please enter: ')
    agent.user_input(query)
    print('-'*50)
```



### Function call

```python
# Function call
from GeneralAgent import Agent

# Function: Get weather information
def get_weather(city: str) -> str:
    """
    get weather information
    @city: str, city name
    @return: str, weather information
    """
    return f"{city} weather: sunny"

agent = Agent('You are a weather assistant', functions=[get_weather])
agent.user_input('What is the weather like in Chengdu?')

# Output
# ```python
# city = "Chengdu"
# weather_info = get_weather(city)
# weather_info
# ```
# The weather in Chengdu is sunny.
# Is there anything else I can help with?
```



### Knowledge Base

```python
# Knowledge Base
from GeneralAgent import Agent

knowledge_files = ['../docs/paper/General_Agent__Self_Call_And_Stack_Memory.pdf']
agent = Agent('You are an AI assistant, reply in Chinese.', workspace='9_knowledge_files', knowledge_files=knowledge_files)
agent.user_input('What does Self call mean?')
```

The knowledge base uses the embedding_texts function in GeneralAgent.skills to embed text by default (the default is OpenAI's text-embedding-3-small model)

You can rewrite the embedding_texts function to use other manufacturers or local embedding methods, as follows:

```python
def new_embedding_texts(texts) -> [[float]]:
    """
    Embedding text arrays
    """
    # Your embedding method
    return result
from GeneralAgent import skills
skills.embedding_texts = new_embedding_texts
```



### Serialization

```python
# Serialization
from GeneralAgent import Agent

# Agent serialization location, LLM messages and python parser status will be automatically saved during operation
workspace='./5_serialize'

role = 'You are a helpful agent.'
agent = Agent(workspace=workspace)
agent.user_input('My name is Shadow.')

agent = None
agent = Agent(role, workspace=workspace)
agent.user_input('What is my name?')
# Output: Your name is Shadow. How can I help you today, Shadow?

# agent: Clear memory + python serialization status
agent.clear()

agent.user_input('What is my name?')
# Output: I'm sorry, but I don't have access to your personal information, including your name. How can I assist you today?

import shutil
shutil.rmtree(workspace)
```

### Workflow

```python
# Workflow: Write a novel
from GeneralAgent import Agent
from GeneralAgent import skills

# Step 0: Define Agent
agent = Agent('You are a novelist')

# Step 1: Get the name and topic of the novel from the user
# topic = skills.input('Please enter the name and topic of the novel: ')
topic = 'The story of the little white rabbit eating candy without brushing its teeth'

# Step 2: Summary of the novel
summary = agent.run(f'The name and topic of the novel are: {topic}, expand and improve the summary of the novel. It is required to be literary, educational, and entertaining. ')

# Step 3: List of chapter names and summaries of the novel
chapters = agent.run('Output the chapter names of the novel and the summary of each chapter, return a list [(chapter_title, chapter_summary), ....]', return_type=list)

# Step 4: Generate detailed content of each chapter of the novel
contents = []
for index, (chapter_title, chapter_summary) in enumerate(chapters):
    content = agent.run(f'For chapters: {chapter_title}\n{chapter_summary}. \nOutput detailed content of the chapter, note that only the content is returned, not the title.')
    content = '\n'.join([x.strip() for x in content.split('\n')])
    contents.append(content)

# Step 5: Format the novel and write it to a file
with open('novel.md', 'w') as f:
    for index in range(len(chapters)):
        f.write(f'### {chapters[index][0]}\n')
        f.write(f'{contents[index]}\n\n')

# Step 6 (optional): Convert markdown file to pdf file

# Step 7: Output novel file to user
skills.output('Your novel has been generated [novel.md](novel.md)\n')
```

### Multi-Agent

```python
# Multi-Agent cooperates to complete the task
from GeneralAgent import Agent
story_writer = Agent('You are a story writer. According to the outline requirements or story outline, return a more detailed story content.')
humor_enhancer = Agent('You are a polisher. Make a story humorous and add humorous elements. Directly output the polished story')

# Disable Python running
story_writer.disable_python_run = True
humor_enhancer.disable_python_run = True

# topic = skills.input('Please enter the outline requirements or story summary of the novel: ')
topic = 'Write a story about a little white rabbit eating candy without brushing its teeth. It has educational significance. '
initial_story = story_writer.run(topic)
enhanced_story = humor_enhancer.run(initial_story)
print(enhanced_story)
```



### LLM switching

Thanks to the GeneralAgent framework's independent function call capability of large model vendors, it can seamlessly switch between different large models to achieve the same capabilities.

The GeneralAgent framework uses the OpenAI Python SDK to support other large models.

```python
from GeneralAgent import Agent

agent = Agent('You are a helpful agent.', model='deepseek-chat', token_limit=32000, api_key='sk-xxx', base_url='https://api.deepseek.com/v1')
agent.user_input('Introduce Chengdu')
```

For details, see: [examples/8_multi_model.py](./examples/8_multi_model.py)

If other large models do not support OpenAI SDK, they can be supported through https://github.com/songquanpeng/one-api.

Or rewrite the llm_inference function in GeneralAgent.skills to use other large models.

```python
from GeneralAgent import skills
def new_llm_inference(messages, model, stream=False, temperature=None, api_key=None, base_url=None):
    """
    Use the large model for inference
    """
    pass
skills.llm_inference = new_llm_inference
```



### Disable Python run

By default, GeneralAgent automatically runs the python code output by LLM.

In some scenarios, if you do not want to run automatically, set `disable_python_run` to `True`.

```python
from GeneralAgent import Agent

agent = Agent('You are a python expert, helping users solve python problems.')
agent.disable_python_run = True
agent.user_input('Use python to implement a function to read files')
```



### More

For more examples, see [examples](./examples)



## Paper

[General Agent: Self Call and Stack Memory](./docs/paper/General_Agent__Self_Call_And_Stack_Memory.pdf)



## Join us👏🏻

Use WeChat to scan the QR code below, join the WeChat group chat, or participate in the contribution.

<p align="center">
<img src="./docs/images/wechat.jpg" alt="wechat" width=400/>
</p>