import os
import sys
# 添加项目根目录到环境变量
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 加载项目配置文件
import dotenv
dotenv.load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), './GeneralAgent/.env'))
# print(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), './GeneralAgent/.env'))
