import re
from collections import OrderedDict
from .interpreter import Interpreter
from GeneralAgent.memory import StackMemoryNode


class PlanInterpreter(Interpreter):
    """
    PlanInterperter is used to parse the plan structure.
    PlanInterpreter handle the input string like this:
    ```runplan
    section1
        section1.1
    ```
    Note: this is only for StackAgent and StackMemory.
    """
    input_match_pattern = '```runplan(.*?)?\n(.*?)\n```'
    
    def __init__(self, memory, max_plan_depth=4) -> None:
        self.memory = memory
        self.max_plan_depth = max_plan_depth

    async def prompt(self, messages) -> str:
        return ''
    
    async def input_parse(self, string) -> (str, bool):
        pattern = re.compile(self.input_match_pattern, re.DOTALL)
        match = pattern.search(string)
        assert match is not None
        prefix = match.group(1).strip()
        structure_data = match.group(2).strip()
        plan_dict = self._structure_plan(structure_data)
        current_node = self.memory.current_node
        self._add_plans_for_node(current_node, plan_dict, prefix)
        return string, False
    
    def _add_plans_for_node(self, node:StackMemoryNode, plan_dict, prefix):
        if self.memory.get_node_level(node) >= self.max_plan_depth:
            return
        for k, v in plan_dict.items():
            new_node = StackMemoryNode(role='system', action='plan', content=k.strip(), prefix=prefix)
            self.memory.add_node_in(node, new_node)
            if len(v) > 0:
                self._add_plans_for_node(new_node, v, prefix)

    @classmethod
    def _structure_plan(cls, data):
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