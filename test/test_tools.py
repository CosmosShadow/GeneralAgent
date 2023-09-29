from base_setting import *
import pytest
from GeneralAgent.tools import google_search, wikipedia_search, scrape_web, Tools

def test_Tools():
    tools = Tools()
    tools.add_funs([google_search, wikipedia_search, scrape_web])
    funs_description = tools.get_funs_description()
    assert 'google_search' in funs_description
    assert 'wikipedia_search' in funs_description
    assert 'scrape_web' in funs_description

def test_google_search():
    result = google_search('apple inc')
    import json
    assert 'apple' in json.dumps(result)

def test_wikipedia_search():
    result = wikipedia_search('apple inc')
    print(result)
    assert 'Steve Jobs' in result

def test_scrape_web():
    url = 'https://tongtianta.ai'
    result = scrape_web(url)
    title = result[0]
    assert 'AI' in title

if __name__ == '__main__':
    # test_Tools()
    # test_google_search()
    # test_wikipedia_search()
    test_scrape_web()