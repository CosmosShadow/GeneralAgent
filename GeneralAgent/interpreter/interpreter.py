# Interpreter
import abc
import re

class Interpreter(metaclass=abc.ABCMeta):
    """
    Interpreter is the base class for all interpreters.
    input_match_pattern is the pattern to match the LLM input string. for example ```tsx\n(.*?)\n```
    output_match_pattern is the pattern to match the LLM ouput string. for example ```tsx\n(.*?)\n```
    output_match_start_pattern is the pattern to match the start of the LLM output string. for example: ```tsx\n
    outptu_parse_done_recall is the callback function to recall when the output_parse is done
    """
    input_match_pattern = None
    output_match_pattern = None
    output_match_start_pattern = None
    outptu_parse_done_recall = None

    def prompt(self, messages) -> str:
        """
        :param messages: list of messages
        :return: string
        """
        return ''
    
    def input_match(self, string) -> bool:
        if self.input_match_pattern is None:
            return False
        match = re.compile(self.input_match_pattern, re.DOTALL).search(string)
        if match is not None:
            return True
        else:
            return False

    def output_match(self, string) -> bool:
        if self.output_match_pattern is None:
            return False
        match = re.compile(self.output_match_pattern, re.DOTALL).search(string)
        if match is not None:
            # 提取匹配后剩余的字符串
            string_left = string[match.end():]
            return True
        else:
            return False
        
    def output_match_start(self, string) -> (bool, str):
        """
        return is_match, string_matched
        """
        if self.output_match_start_pattern is None:
            return False, ''
        match = re.compile(self.output_match_start_pattern, re.DOTALL).search(string)
        if match is not None:
            string_matched = string[match.start():]
            return True, string_matched
        else:
            return False, ''
        
    def output_match_end(self, string) -> (bool, str):
        """
        return is_match, string_matched
        """
        if self.output_match_pattern is None:
            return False, ''
        match = re.compile(self.output_match_pattern, re.DOTALL).search(string)
        if match is not None:
            string_left = string[match.end():]
            return True, string_left
        else:
            return False, ''
        
    def input_parse(self, string) -> (str, bool):
        """
        parse the input、output string, and return the output string and is_stop
        """
        return '', False

    def output_parse(self, string) -> (str, bool):
        """
        parse the input、output string, and return the output string and is_stop
        """
        return '', False
    
