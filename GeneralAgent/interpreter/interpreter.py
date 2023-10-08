# Interpreter
import abc
import re

class Interpreter(metaclass=abc.ABCMeta):
    def prompt(self, messages) -> str:
        """
        :param messages: list of messages
        :return: string
        """
        return ''

    @property
    @abc.abstractmethod
    def match_template(self) -> bool:
        """
        the patten to match the input string、output string
        """
        pass

    def match(self, string) -> bool:
        match = re.compile(self.match_template, re.DOTALL).search(string)
        if match is not None:
            return True
        else:
            return False

    @abc.abstractmethod
    def parse(self, string) -> (str, bool):
        """
        parse the input、output string, and return the output string and is_stop
        """
        pass