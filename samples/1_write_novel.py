from GeneralAgent.agent import Agent
from GeneralAgent import skills

agent = Agent.with_functions(role_prompt=f'你是一个小说家', new=True, continue_run=False, self_control=False)
# topic = skills.input('请输入小说的名称和主题: ')
topic = '小白兔吃糖不刷牙的故事'
summary = agent.run(f'小说的名称和主题是: {topic}，扩展和完善一下小说概要。要求具备文艺性、教育性、娱乐性。', return_type=str)
outline = agent.run('输出小说的章节名称和每个章节的概要，返回列表 [(chapter_title, chapter_summary), ....]', return_type=list)
chapters = []
for index, (title, summary) in enumerate(outline):
    chapter = agent.run(f'对于章节: {title}，{summary}. \n输出章节的详细内容. 注意只返回内容，不要标题。', return_type=str)
    chapters.append(chapter)
with open('novel.md', 'w') as f:
    for index in range(len(outline)):
        f.write(f'### {outline[index][0]}\n{chapters[index]}\n\n')
skills.output('你的小说已经生成[novel.md](novel.md)\n')