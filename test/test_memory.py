# 测试Memory
from base_setting import *
from GeneralAgent.memory import Memory, get_memory_importance_score

def test_get_memory_importance_score():
    rating = get_memory_importance_score('buying groceries at The Willows Market and Pharmacy')
    assert rating <= 3

    rating = get_memory_importance_score('buy a house')
    assert rating >= 8


if __name__ == '__main__':
    test_get_memory_importance_score()
    # test_memory()