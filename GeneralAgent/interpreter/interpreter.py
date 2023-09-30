# Interpreter
import abc
import re

class Interpreter(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def prompt(self, messages) -> str:
        pass

    @property
    @abc.abstractmethod
    def match_template(self) -> bool:
        pass

    def match(self, string) -> bool:
        match = re.compile(self.match_template, re.DOTALL).search(string)
        if match is not None:
            return True
        else:
            return False

    @abc.abstractmethod
    def parse(self, string) -> (str, bool):
        # return output, is_stop
        pass