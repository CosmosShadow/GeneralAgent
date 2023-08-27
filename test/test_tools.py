from base_setting import *
from GeneralAgent.tools import google_search, wikipedia_search


def test_google_search():
    result = google_search('apple inc')
    # print(result)
    assert 'https://www.apple.com/' in result

def test_wikipedia_search():
    result = wikipedia_search('apple inc')
    assert 'Steve Jobs' in result

if __name__ == '__main__':
    test_google_search()
    # test_wikipedia_search()