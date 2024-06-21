# agent.run命令的时候，核对生成内容是否合适
from GeneralAgent import Agent
from GeneralAgent import skills

# 步骤0: 定义Agent
agent = Agent('你是一个小说家')

# 步骤1: 从用户处获取小说的名称和主题
# topic = skills.input('请输入小说的名称和主题: ')
topic = '小白兔吃糖不刷牙的故事'

# 步骤2: 小说的概要
summary = agent.run(f'小说的名称和主题是: {topic}，扩展和完善一下小说概要。要求具备文艺性、教育性、娱乐性。')

# 步骤3: 小说的章节名称和概要列表
chapters = agent.run('输出小说的章节名称和每个章节的概要，返回列表 [(chapter_title, chapter_summary), ....]', return_type=list, user_check=True)

# 步骤4: 生成小说每一章节的详细内容
agent.disable_python()
contents = []
for index, (chapter_title, chapter_summary) in enumerate(chapters):
    content = agent.run(f'对于章节: {chapter_title}\n概要: {chapter_summary}. \n写小说这个章节的详细内容，注意只返回内容，不要标题。')
    content = '\n'.join([x.strip() for x in content.split('\n')])
    contents.append(content)

# 步骤5: 将小说格式化写入文件
with open('novel.md', 'w') as f:
    for index in range(len(chapters)):
        f.write(f'### {chapters[index][0]}\n')
        f.write(f'{contents[index]}\n\n')

# 步骤6(可选): 将markdown文件转换为pdf文件

# 步骤7: 输出小说文件给用户
skills.output('你的小说已经生成[novel.md](novel.md)\n')