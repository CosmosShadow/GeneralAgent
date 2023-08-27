from base_setting import *
from GeneralAgent.tools import google_search, wikipedia_search, scrape_web


def test_google_search():
    result = google_search('apple inc')
    # print(result)
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

if __name__ == '__main__':
    # test_google_search()
    # test_wikipedia_search()
    test_scrape_web()