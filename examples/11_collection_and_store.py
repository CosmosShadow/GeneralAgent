# 多轮对话搜集信息 & 保存
from GeneralAgent import Agent
from dotenv import load_dotenv

load_dotenv()

role = """
你是一个专业的诊前护士。
你的主要工作: 和病人沟通，确认详细的病情，保存病历。

# 1、病情沟通例子
用户: 我眼睛疼
你: 疼多旧了？
用户: 2天
你: 你还可以看见东西吗？视力有没有影响？
用户: 还能看见
你: ....

当病情确认，直接输出python代码，使用 save_medical_record 函数保存病历详情。

medical_record = \"\"\"
主诉： 眼睛干涩
现病史： 最近长时间使用电子设备
既往史： 无特殊情况
过敏史： 无过敏史
家族史： 无家族史
个人史： 生活环境比较潮湿，未使用任何眼睛滴剂或药物缓解症状
\"\"\"
save_medical_record(medical_record)

"""

stop = False
# 保存病历函数
def save_medical_record(medical_record): 
    """
    保存病历
    @param medical_record: 病历内容
    """
    # print(medical_record)
    with open('medical_record.txt', 'a') as f:
        f.write(medical_record)
    global stop
    stop = True
    return "病历已保存"


agent = Agent(role, functions=[save_medical_record], hide_python_code=True)
agent.user_input('你可以做什么?')
while not stop:
    query = input('请输入: ')
    agent.user_input(query)