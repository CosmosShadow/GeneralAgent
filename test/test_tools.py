from base_setting import *
from GeneralAgent.tools import google_search, wikipedia_search, scrape_web, Tools


def test_google_search():
    result = google_search('apple inc')
    import json
    assert 'apple' in json.dumps(result)

def test_wikipedia_search():
    result = wikipedia_search('apple inc')
    print(result)
    assert 'Steve Jobs' in result

def test_scrape_web():
    url = 'https://www.baidu.com'
    soup = scrape_web(url)
    title = soup.title.string
    assert '百度一下，你就知道' == title

def test_Tools():
    tools = Tools()
    tools.add_funs([google_search, wikipedia_search, scrape_web])
    print(tools.get_funs_description())

if __name__ == '__main__':
    # test_google_search()
    # test_wikipedia_search()
    # test_scrape_web()
    test_Tools()