import pytest
import asyncio

def test_parse_segment_llm_result():
    from skills.memory_utils import _parse_segment_llm_result
    string = "<<Nougat: Neural Optical Understanding for Academic Documents>>\n0: 15\n\n<<Abstract>>\n6: 15\n\n<<Introduction>>\n17: 32\n\n<<Primary Contributions>>\n34: 38"
    nodes = _parse_segment_llm_result(string)
    assert nodes['Abstract'] == (6, 15)
    assert len(nodes) == 4

if __name__ == '__main__':
    test_parse_segment_llm_result()