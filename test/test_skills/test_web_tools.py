def test_google_search():
    from GeneralAgent import skills
    result = skills.google_search('apple inc founding time')
    assert '1976' in result

# def test_wikipedia_search():
#     from GeneralAgent import skills
#     result = skills.wikipedia_search('apple inc')
#     print(result)
#     assert 'Steve Jobs' in result

def test_scrape_web():
    from GeneralAgent import skills
    url = 'https://www.baidu.com'
    result = skills.scrape_web(url)
    assert '百度' in result


if __name__ == '__main__':
    test_google_search()
    test_scrape_web()