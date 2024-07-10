# GeneralAgent: From LLM to Agent

<p align="center">
<a href="README.md"><img src="https://img.shields.io/badge/文档-中文版-blue.svg" alt="CN doc"></a>
<a href="README_EN.md"><img src="https://img.shields.io/badge/document-English-blue.svg" alt="EN doc"></a>
</p>

GeneralAgent is a Python-native Agent framework that aims to seamlessly integrate large language models with Python.

**Main features**

* **Tool call**: GeneralAgent does not rely on the function call of large models, but calls tools through the python code interpreter.

* **Serialization**: GeneralAgent supports serialization, including memory and python execution status, and is ready to use

* **Self-call(experimental)**: GeneralAgent minimizes the number of calls to large models through self-call and stack memory to efficiently handle complex tasks. For more details, please see our [paper](./docs/paper/General_Agent__Self_Call_And_Stack_Memory.pdf)

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
# export OPENAI_API_BASE=your_openai_base_url
# using with not openai official server or using other OpenAI API formate LLM server such as deepseek, zhipu(chatglm),qwen, etc.
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

### Write a novel

```python
# Write a novel
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



### Multimodal input

The input parameter of user_input and the command parameter of run support strings or arrays.

Multimodal is supported when the array is used. The format is the simplest mode: ['text_content', {'image': 'path/to/image'}, ...]

```python
# Multimodal support: Image input
from GeneralAgent import Agent

agent = Agent('You are a helpful assistant.')
agent.user_input(['what is in the image?', {'image': '../docs/images/self_call.png'}])
```




### LLM switching

#### OpenAI SDK

Thanks to the GeneralAgent framework's independent function call capability of large model vendors, it can seamlessly switch between different large models to achieve the same capabilities.

The GeneralAgent framework uses the OpenAI Python SDK to support other large models.

```python
from GeneralAgent import Agent

agent = Agent('You are a helpful agent.', model='deepseek-chat', token_limit=32000, api_key='sk-xxx', base_url='https://api.deepseek.com/v1')
agent.user_input('Introduce Chengdu')
```

For details, see: [examples/8_multi_model.py](./examples/8_multi_model.py)

#### Azure OpenAI 

```python
from GeneralAgent import Agent

# api_key = os.getenv("OPENAI_API_KEY")
# base_url = os.getenv("OPENAI_API_BASE")
api_key = '8ef0b4df45e444079cd5xxx' # Azure API Key or use OPENAI_API_KEY environment variable
base_url = 'https://xxxx.openai.azure.com/' # Azure API Base URL or use OPENAI_API_BASE environment variable
model = 'azure_cpgpt4' # azure_ with model name, e.g. azure_cpgpt4
# azure api_version is default to '2024-05-01-preview'. You can set by environment variable AZURE_API_VERSION

agent = Agent('You are a helpful assistant', api_key=api_key, base_url=base_url, model=model)
while True:
    query = input('Please input your query:')
    agent.user_input(query)
    print('-'*50)
```


#### One API

If other large models do not support OpenAI SDK, they can be supported through https://github.com/songquanpeng/one-api.


#### Custom large model

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



### Hide Python Run

In formal business scenarios, if you do not want users to see the running of Python code but only the final result, you can set `hide_python_code` to `True`.

```python
from GeneralAgent import Agent
agent = Agent('You are a helpful assistant.', hide_python_code=True)
agent.user_input('caculate 0.999 ** 1000')
```



### AI search

```python
# AI search
# Prerequisites:
# 1. Please configure the environment variable SERPER_API_KEY (https://serper.dev/'s API KEY);
# 2. Install the selenium library: pip install selenium

from GeneralAgent import Agent
from GeneralAgent import skills

google_results = []

# Step 1: First Google search
question = input('Please enter a question and proceed AI search: ')
content1 = skills.google_search(question)
google_results.append(content1)

# Step 2: Second Google search: According to the first search structure, get the question to continue searching
agent = Agent('You are an AI search assistant.')
queries = agent.run(f'User question: \n{question}\n\nSearch engine results: \n{content1}\n\n. Can you help users, what are the key phrases that need to be searched (up to 3, and not too overlapping with the question itself)? Return the key phrase list variable ([query1, query2])', return_type=list)
print(queries)
for query in queries:
content = skills.google_search(query)
google_results.append(content)

# Step 3: Extract key web page content
agent.clear()
web_contents = []
google_result = '\n\n'.join(google_results)
urls = agent.run(f'User question: \n{question}\n\nSearch engine result: \n{google_result}\n\n. Which web pages are more helpful for user questions? Please return the most important webpage url list variable ([url1, url2, ...])', return_type=list)
for url in urls:
content = skills.web_get_text(url, wait_time=2)
web_contents.append(content)

# Step 4: Output results
agent.clear()
web_content = '\n\n'.join(web_contents)
agent.run(f'User question: \n{question}\n\nSearch engine results: \n{google_result}\n\nPart of the webpage content: \n{web_content}\n\n. Please give the user a detailed answer based on the user's question, search engine results, and webpage content. It is required to be output according to a certain directory structure and use markdown format.')
```



### More

For more examples, see [examples](./examples)


## API

### Basic Usage

**Agent.\__init__(self, role: str, workspace: str = None, functions: List[Callable] = [], knowledge_files: List[str] = None)**

Initializes an Agent instance.

- role (str): The role of the agent.
- workspace (str, optional): The agent's workspace. Default is None (not serialized). If a directory is specified, the agent will automatically save the agent's state and reload it upon the next initialization.
- functions (List[Callable], optional): A list of functions that the agent can call.
- knowledge_files (List[str], optional): A list of file paths for the agent's knowledge base.


**Agent.run(self, command: Union[str, List[Union[str, Dict[str, str]]]], return_type: str = str, display: bool = False)**

Executes a command and returns the result in the specified return type.

- command (Union[str, List[Union[str, Dict[str, str]]]]): The command to execute. Examples: 'describe chengdu' or ['what is in image?', {'image': 'path/to/image'}].
- return_type (str, optional): The return type of the result. Default is str.
- display (bool, optional): Whether to display the intermediate content generated by the LLM. Default is False.


**Agent.user_input(self, input: Union[str, List[Union[str, Dict[str, str]]]])**

Responds to user input and always displays the intermediate content generated by the LLM.

- input (Union[str, List[Union[str, Dict[str, str]]]]): The user input.


**Agent.clear(self)**

Clears the agent's state.



### Advanced Usage

[] # TODO




## Paper

[General Agent: Self Call and Stack Memory](./docs/paper/General_Agent__Self_Call_And_Stack_Memory.pdf)



## Join us👏🏻

Use WeChat to scan the QR code below, join the WeChat group chat, or participate in the contribution.

<p align="center">
<img src="./docs/images/wechat.jpg" alt="wechat" width=400/>
</p>