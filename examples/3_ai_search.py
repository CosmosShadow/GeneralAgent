# AI搜索
# 运行前置条件: 
# 1. 请先配置环境变量 SERPER_API_KEY (https://serper.dev/ 的API KEY)；
# 2. 安装 selenium 库: pip install selenium

from GeneralAgent import Agent
from GeneralAgent import skills

google_results = []

# 步骤1: 第一次google搜索
question = input('请输入问题，进行 AI 搜索: ')
# question = '周鸿祎卖车'
content1 = skills.google_search(question)
google_results.append(content1)

# 步骤2: 第二次google搜索: 根据第一次搜索结构，获取继续搜索的问题
agent = Agent('你是一个AI搜索助手。')
querys = agent.run(f'用户问题: \n{question}\n\n搜索引擎结果: \n{content1}\n\n。请问可以帮助用户，需要继续搜索的关键短语有哪些(最多3个，且和问题本身不太重合)？返回关键短语列表变量([query1, query2])', return_type=list)
print(querys)
for query in querys:
    content = skills.google_search(query)
    google_results.append(content)

# 步骤3: 提取重点网页内容
agent.clear()
web_contents = []
google_result = '\n\n'.join(google_results)
urls = agent.run(f'用户问题: \n{question}\n\n搜索引擎结果: \n{google_result}\n\n。哪些网页对于用户问题比较有帮助？请返回最重要的不超过5个的网页url列表变量([url1, url2, ...])', return_type=list)
for url in urls:
    print(url)
    content = skills.web_get_text(url, wait_time=2)
    web_contents.append(content)

# 步骤4: 输出结果
agent.clear()
web_content = '\n\n'.join(web_contents)
agent.run(f'用户问题: \n{question}\n\n搜索引擎结果: \n{google_result}\n\n部分网页内容: \n{web_content}\n\n。请根据用户问题，搜索引擎结果，网页内容，给出用户详细的回答，要求按一定目录结构来输出，并且使用markdown格式。')