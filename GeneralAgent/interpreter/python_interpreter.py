import re, io, os, sys, ast
import pickle
import logging
from jinja2 import Template
from functools import partial
from .interpreter import Interpreter


def get_python_version() -> str:
    """
    Return the python version, like "3.9.12"
    """
    import platform

    python_version = platform.python_version()
    return python_version


def get_function_signature(func, module: str = None):
    """Returns a description string of function"""
    try:
        import inspect

        sig = inspect.signature(func)
        sig_str = str(sig)
        desc = f"{func.__name__}{sig_str}"
        if func.__doc__:
            desc += ": " + func.__doc__.strip()
        if module is not None:
            desc = f"{module}.{desc}"
        if inspect.iscoroutinefunction(func):
            desc = "" + desc
        return desc
    except Exception as e:
        import logging

        logging.exception(e)
        return ""


default_import_code = """
import os, sys, math, time
from codyer import skills
"""


class PythonInterpreter(Interpreter):
    """
    Python Interpreter: run python code in the interpreter. Not same namespace with the agent & Can Only run synchronous code
    """

    output_match_pattern = "```python\n#run code\n(.*?)\n```"
    agent = None

    python_prompt_template = """
# Run python code
- format: ```python\n#run code\nyour code\n```. Only this format will be executed.
- Every time you output code, you need to reimport the required library. Each execution only shares variables and functions, without including libraries.
- Available libraries: {{python_libs}}
- The following functions can be used in code (already implemented and imported for you, do not import them again):
```
{{python_funcs}}
```
- Example:
```python
#run code
result = 1 + 1
result
```

# Show python code
- format: ```python\n#show code\nyour code\n```. This format will be displayed.
- Example:
```python
#show code
print('Hello, world!')
```
"""

    function_tools = []

    def __init__(
        self,
        agent=None,
        serialize_path: str = None,
        libs: str = "",
        import_code: str = None,
        prompt_append="",
        stop_wrong_count=3,
    ):
        """
        @serialize_path (str): python解释器的序列化路径，如果为None，则不序列化。举例: './python_interpreter.bin' or 'serialized.pkl'
        @lib (str, optional): 可以使用的库
        @import_code (str, optional): code to import. The tools used should be imported. Defaults to default_import_code.
        @prompt_append: append to the prompt, custom prompt can be added here
        @stop_wrong_count: stop running when the code is wrong for stop_wrong_count times
        """
        self.globals = {}  # global variables shared by all code
        self.agent = agent
        self.python_libs = libs
        self.import_code = import_code or default_import_code
        self.serialize_path = serialize_path
        self.prompt_append = prompt_append
        # self.tools = tools or Tools([])
        self.globals = self.load()
        # count the number of times the code is wrong, and stop running when it reaches the threshold
        self.run_wrong_count = 0
        self.stop_wrong_count = stop_wrong_count

    def load(self):
        if self.serialize_path is None:
            return {}
        if os.path.exists(self.serialize_path):
            with open(self.serialize_path, "rb") as f:
                data = pickle.loads(f.read())
                return data["globals"]
        return {}

    def prompt(self, messages) -> str:
        funtions = "\n\n".join([get_function_signature(x) for x in self.function_tools])
        variables = {
            "python_libs": self.python_libs,
            "python_funcs": funtions,
            "python_version": get_python_version(),
        }
        return (
            Template(self.python_prompt_template).render(**variables)
            + self.prompt_append
        )

    def save(self):
        if self.serialize_path is None:
            return
        save_globals = self._remove_unpickleable()
        # save
        with open(self.serialize_path, "wb") as f:
            data = {"globals": save_globals}
            f.write(pickle.dumps(data))

    def _remove_unpickleable(self):
        save_globals = self.globals.copy()
        if "__builtins__" in save_globals:
            save_globals.__delitem__("__builtins__")
        keys = list(save_globals.keys())
        for key in keys:
            try:
                pickle.dumps(save_globals[key])
            except Exception as e:
                save_globals.__delitem__(key)
        return save_globals

    def output_parse(self, string) -> (str, bool):
        pattern = re.compile(self.output_match_pattern, re.DOTALL)
        match = pattern.search(string)
        assert match is not None
        result, stop = self.run_code(match.group(1))
        result = (
            "\nThe execution of the python code is completed, and the result is as follows:\n"
            + result
            + "\n"
        )
        return result, stop

    def run_code(self, code):
        code = self.import_code + "\n" + code
        logging.debug(code)

        output = io.StringIO()
        sys.stdout = output

        try:
            if self.agent is not None:
                self.agent.run_level += 1
                if self.agent is not None:
                    self.globals["agent"] = self.agent
            for fun in self.function_tools:
                # partial function default is remote function
                if isinstance(fun, partial):
                    name = fun.args[0]
                else:
                    name = fun.__name__
                self.globals[name] = fun
            result = exec_and_get_last_expression(self.globals, code)
            self.run_wrong_count = 0
            stop = True
            # 出现了自我调用，则判断一下层级，如果层级为1，则停止
            if self.agent is not None:
                stop = self.agent.run_level >= 1
                self.agent.python_run_result = result
            if result is None:
                result = output.getvalue()
            else:
                if output.getvalue().strip() != "":
                    result = output.getvalue() + "\n" + str(result)
            return str(result), stop
        except Exception as e:
            logging.exception(e)
            import traceback

            error = traceback.format_exc()
            self.run_wrong_count += 1
            if self.run_wrong_count >= self.stop_wrong_count:
                raise e
            return error, False
        finally:
            self.save()
            sys.stdout = sys.__stdout__
            if self.agent is not None:
                self.agent.run_level -= 1

    def get_variable(self, name):
        if name in self.globals:
            return self.globals[name]
        else:
            logging.warning(f"Variable {name} not found")
            return None

    def set_variable(self, name, value):
        self.globals[name] = value


def exec_and_get_last_expression(globals_vars, code):
    tree = ast.parse(code)

    try:
        last_node = tree.body[-1]
        code_body = tree.body[0:-1]
        last_expr = ast.unparse(last_node)

        if isinstance(last_node, ast.Assign):
            code_body = tree.body
            expr_left = last_node.targets[-1]
            if isinstance(expr_left, ast.Tuple):
                last_expr = f"({', '.join([x.id for x in expr_left.elts])})"
            else:
                last_expr = expr_left.id

        elif isinstance(last_node, ast.AugAssign) or isinstance(
            last_node, ast.AnnAssign
        ):
            code_body = tree.body
            last_expr = last_node.target.id

        if len(code_body):
            main_code = compile(ast.unparse(code_body), "<string>", "exec")
            exec(main_code, globals_vars)
    except SyntaxError:
        return None

    try:
        return eval(
            compile(last_expr, "<string>", "eval"),
            globals_vars,
        )
    except SyntaxError:
        return None
