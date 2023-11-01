from GeneralAgent.tools import Tools

def test_Tools():
    from GeneralAgent import skills
    tools = Tools()
    tools.add_funs([skills.google_search, skills.wikipedia_search, skills.scrape_web])
    funs_description = tools.get_funs_description()
    assert 'google_search' in funs_description
    assert 'wikipedia_search' in funs_description
    assert 'scrape_web' in funs_description

def test_google_search():
    from GeneralAgent import skills
    result = skills.google_search('apple inc')
    import json
    assert 'apple' in json.dumps(result)

def test_wikipedia_search():
    from GeneralAgent import skills
    result = skills.wikipedia_search('apple inc')
    print(result)
    assert 'Steve Jobs' in result

def test_scrape_web():
    from GeneralAgent import skills
    url = 'https://tongtianta.ai'
    result = skills.scrape_web(url)
    title = result[0]
    assert 'AI' in title

if __name__ == '__main__':
    # test_Tools()
    # test_google_search()
    # test_wikipedia_search()
    test_scrape_web()