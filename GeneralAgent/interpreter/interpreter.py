# Interpreter
import abc
import re

class Interpreter(metaclass=abc.ABCMeta):
    """
    Interpreter is the base class for all interpreters.
    output_match_pattern is the pattern to match the LLM ouput string. for example ```tsx\n(.*?)\n```
    """
    output_match_pattern = None

    def prompt(self, messages) -> str:
        """
        :param messages: list of messages
        :return: string
        """
        return ''

    def output_match(self, string) -> bool:
        if self.output_match_pattern is None:
            return False
        match = re.compile(self.output_match_pattern, re.DOTALL).search(string)
        if match is not None:
            return True
        else:
            return False

    def output_parse(self, string) -> (str, bool):
        """
        parse the input、output string, and return the output string and is_stop
        """
        return '', False