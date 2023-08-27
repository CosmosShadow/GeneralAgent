# 控制器
# 用于控制整个系统的运行
from memory import Memory, ConceptNode
from code import CodeWorkspace
from tools import Tools
from llm import embedding_fun
from pydantic import BaseModel

class RoleSetting(BaseModel):
    """角色设定"""
    name: str
    profile: str
    goal: str
    constraints: str # 约束
    desc: str


class Controller:
    def __init__(self, role_setting, workspace, send_message_fun):
        # role_setting: 角色设定
        # workspace: 工作空间
        self.role_setting = role_setting
        self.workspace = workspace
        meory_file_path = f'{workspace}/memory.json'
        code_serialize_path = f'{workspace}/code.bin'
        self.memory = Memory(meory_file_path, embedding_fun)
        self.code_workspace = CodeWorkspace(code_serialize_path)
        self.tools = Tools(send_message_fun)

    def input(self, user_input):
        # TODO: input的逻辑可能有问题，比如澄清用户需求的时候，用户输入的内容可能是不完整的，这时候就需要澄清用户需求，然后再次输入，就不能全局执行下面的流程
        # TODO: 循环流程需要简单的状态机来控制
        # 用户输入
        intput_concept = self.memory.add_concept('input', user_input)
        # 正对新输入，做计划
        self._plan_for_new_input()
        # 针对旧计划，做计划
        self._plan_for_old_plan()
        # 执行内容
        self._action()
        # 更新Done ??
        intput_concept.state = 'done'
        self.memory.update_concept(intput_concept)

    def _plan_for_new_input(self):
        prompt = """xxxx"""
        new_plans = []
        for new_plan in new_plans:
            self.memory.add_concept('plan', new_plan)
    
    def _action(self):
        # 执行计划
        # TODO: 获取plan，执行plan
        # how to cancel plan?
        # 当询问用户问题的的时候(澄清)，如何停止执行，等待用户新的输入
        plans = self.memory.get_plan()
        for plan in plans:
            self._action_one(plan)

    def _action_one(self, plan: ConceptNode):
        # TODO
        if plan.concept.startswith('[plan]'):
            pass
        if plan.concept.startswith('[action]'):
            pass
        # if plan.concept.startswith('[thought]'):
        #     pass
        if plan.concept.startswith('[response]'):
            # TODO: 回复用户，有可能是最终答案，也可能是中间问题，想获取更多信息
            pass

    def _run_command(self, command):
        # 输入命令(string)，生成代码并执行
        retry_count = 3
        # 生成代码
        code = self._code_generate(command)
        # 检查&修复代码
        for index in range(retry_count):
            check_success = self._code_check(command, code)
            if check_success: break
            if index == retry_count - 1: return False
            code = self._code_fix(code, command=command)
        # 执行代码&修复代码
        for index in range(retry_count):
            run_success, sys_stdio = self.code_workspace.run_code(command, code)
            if run_success: break
            if index == retry_count - 1: return False
            code = self._code_fix(code, command=command, error=sys_stdio)
        return run_success

    def _code_generate(self, command):
        # 根据命令，生成执行的代码
        # TODO
        code = ''
        return code

    def _code_check(self, command, code):
        # TODO: 
        # 验证代码是否可以执行，有没有什么问题
        return True
    
    def _code_fix(self, code, command=None, error=None):
        # TODO: 
        # 根据command，修复代码
        return code