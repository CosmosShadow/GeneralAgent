# Interpreter
import abc
import re

class Interpreter(metaclass=abc.ABCMeta):
    """
    Interpreter is the base class for all interpreters.
    match_pattern is the pattern to match the input string. for example ```tsx\n(.*?)\n```
    match_start_pattern is the pattern to match the start of the input string. for example: ```tsx\n
    """

    match_start_pattern = None
    match_pattern = None

    async def prompt(self, messages) -> str:
        """
        :param messages: list of messages
        :return: string
        """
        return ''

    def match(self, string) -> bool:
        if self.match_pattern is None:
            return False
        match = re.compile(self.match_pattern, re.DOTALL).search(string)
        if match is not None:
            return True
        else:
            return False
        
    def match_start(self, string) -> (bool, str):
        """
        return is_match, string_matched
        """
        if self.match_start_pattern is None:
            return False, ''
        match = re.compile(self.match_start_pattern, re.DOTALL).search(string)
        if match is not None:
            string_matched = string[match.start():]
            return True, string_matched
        else:
            return False, ''
        
    def match_end(self, string) -> (bool, str):
        """
        return is_match, string_matched
        """
        if self.match_pattern is None:
            return False, ''
        match = re.compile(self.match_pattern, re.DOTALL).search(string)
        if match is not None:
            string_left = string[match.end():]
            return True, string_left
        else:
            return False, ''

    async def parse(self, string) -> (str, bool):
        """
        parse the input、output string, and return the output string and is_stop
        """
        return '', False