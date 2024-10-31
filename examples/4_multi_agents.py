# 多Agent配合完成任务
from GeneralAgent import Agent
from dotenv import load_dotenv

load_dotenv()
story_writer = Agent('你是一个故事创作家，根据大纲要求或者故事梗概，返回一个更加详细的故事内容。')
humor_enhancer = Agent('你是一个润色作家，将一个故事进行诙谐润色，增加幽默元素。直接输出润色后的故事')

# 禁用Python运行
story_writer.disable_python_run = True
humor_enhancer.disable_python_run = True

# topic = skills.input('请输入小说的大纲要求或者故事梗概: ')
topic = '写个小白兔吃糖不刷牙的故事，有教育意义。'
initial_story = story_writer.run(topic)
enhanced_story = humor_enhancer.run(initial_story)
print(enhanced_story)