import re
from collections import OrderedDict
from .interpreter import Interpreter
from GeneralAgent.memory import MemoryNode


class PlanInterpreter(Interpreter):
    def __init__(self, memory, max_plan_depth=4) -> None:
        self.memory = memory
        self.max_plan_depth = max_plan_depth

    def prompt(self, messages) -> str:
        return ''

    @property
    def match_template(self):
        return '```runplan(.*?)?\n(.*?)\n```'
    
    def parse(self, string):
        pattern = re.compile(self.match_template, re.DOTALL)
        match = pattern.search(string)
        assert match is not None
        prefix = match.group(1).strip()
        structure_data = match.group(2).strip()
        plan_dict = self.structure_plan(structure_data)
        current_node = self.memory.current_node
        self.add_plans_for_node(current_node, plan_dict, prefix)
        return string, False
    
    def add_plans_for_node(self, node:MemoryNode, plan_dict, prefix):
        if self.memory.get_node_level(node) >= self.max_plan_depth:
            return
        for k, v in plan_dict.items():
            new_node = MemoryNode(role='system', action='plan', content=k.strip(), prefix=prefix)
            self.memory.add_node_in(node, new_node)
            if len(v) > 0:
                self.add_plans_for_node(new_node, v, prefix)

    @classmethod
    def structure_plan(cls, data):
        structured_data = OrderedDict()
        current_section = [structured_data]
        for line in data.split('\n'):
            if not line.strip():
                continue
            depth = line.count('    ')
            section = line.strip()
            while depth < len(current_section) - 1:
                current_section.pop()
            current_section[-1][section] = OrderedDict()
            current_section.append(current_section[-1][section])
        return structured_data