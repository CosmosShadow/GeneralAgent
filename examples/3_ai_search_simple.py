# def main(messages, input, files, output_callback, event=None, workspace='./'):

# question = input('')
question = '周鸿祎卖车'
from GeneralAgent import Agent
from GeneralAgent import skills

agent = Agent('You are an AI search assistant.')

# Google search
google_result = skills.google_search(question)

# Get important web
urls = agent.run(f'User question: {question}\nSearch results: {google_result}\nReturn up to 5 most relevant URLs.', return_type=list)
web_content = '\n\n'.join([skills.web_get_text(url, wait_time=2) for url in urls])

# Display the answer
agent.clear()
agent.run(f'User question: {question}\nSearch results: {google_result}\nWeb content: {web_content}\nProvide a detailed answer in markdown format.', display=True)