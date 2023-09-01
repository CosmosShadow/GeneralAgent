from base_setting import *
from GeneralAgent.tools import google_search, wikipedia_search, scrape_web, Tools


def test_google_search():
    result = google_search('apple inc')
    print(result)
    assert 'https://www.apple.com/' in result

def test_wikipedia_search():
    result = wikipedia_search('apple inc')
    assert 'Steve Jobs' in result

def test_scrape_web():
    # url = 'https://www.baidu.com'
    url = 'https://tongtianta.ai'
    title, text, links = scrape_web(url)
    assert title == '通天塔AI'
    assert '通天塔AI' in text
    assert links == []

def test_Tools():
    tools = Tools()
    tools.add_funs([google_search, wikipedia_search, scrape_web])
    print(tools.get_funs_description())

if __name__ == '__main__':
    # test_google_search()
    # test_wikipedia_search()
    # test_scrape_web()
    test_Tools()