from base_setting import *
from GeneralAgent.memory import LinkMemory
from GeneralAgent.memory.memory_utils import parse_segment_llm_result
from GeneralAgent.utils import default_output_recall
import asyncio
import pytest
import fitz

def test_parse_segment_llm_result():
    string = "<<Nougat: Neural Optical Understanding for Academic Documents>>\n0: 15\n\n<<Abstract>>\n6: 15\n\n<<Introduction>>\n17: 32\n\n<<Primary Contributions>>\n34: 38"
    nodes = parse_segment_llm_result(string)
    assert nodes['Abstract'] == (6, 15)
    assert len(nodes) == 4

if __name__ == '__main__':
    test_parse_segment_llm_result()