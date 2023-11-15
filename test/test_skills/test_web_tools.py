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
    # test_search_functions()
    # test_edit_llm_function()
    pass