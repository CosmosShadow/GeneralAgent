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
    url = 'https://www.baidu.com'
    text, links = scrape_web(url)
    print(text)
    print(links)

if __name__ == '__main__':
    # test_google_search()
    # test_wikipedia_search()
    test_scrape_web()