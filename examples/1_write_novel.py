# 写小说
from GeneralAgent.agent import Agent
from GeneralAgent import skills

agent = Agent('你是一个小说家')
# topic = skills.input('请输入小说的名称和主题: ')
topic = '小白兔吃糖不刷牙的故事'
summary = agent.run(f'小说的名称和主题是: {topic}，扩展和完善一下小说概要。要求具备文艺性、教育性、娱乐性。', return_type=str)
chapters = agent.run('输出小说的章节名称和每个章节的概要，返回列表 [(chapter_title, chapter_summary), ....]', return_type=list)
contents = []
for index, (chapter_title, chapter_summary) in enumerate(chapters):
    content = agent.run(f'对于章节: {chapter_title}\n{chapter_summary}. \n输出章节的详细内容，注意只返回内容，不要标题。', return_type=str)
    content = '\n'.join([x.strip() for x in content.split('\n')])
    contents.append(content)
with open('novel.md', 'w') as f:
    for index in range(len(chapters)):
        f.write(f'### {chapters[index][0]}\n')
        f.write(f'{contents[index]}\n\n')
skills.output('你的小说已经生成[novel.md](novel.md)\n')

# 删除Agent: 记忆文件 + python序列化状态
# agent.delete()