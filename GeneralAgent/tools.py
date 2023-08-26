# 工具集，code可以操作的东西

class Tools():
    def __init__(self, send_message_fun):
        self.funs = {}
        # send_message_fun(type, content)
        # 发送消息的函数，参数为消息内容
        # type: text、react、json
        # 可以是markdown的文本、也可以是一块react的代码、json
        self.funs['send_message'] = send_message_fun
