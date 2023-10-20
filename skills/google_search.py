def google_search(query: str) -> dict:
    """
    google search with query, return a result in list like [{"title": "xx", "link": "xx", "snippet": "xx"}]
    """
    import os
    import json
    import requests
    SERPER_API_KEY = os.environ.get('SERPER_API_KEY', None)
    if SERPER_API_KEY is None:
        print('Please set SERPER_API_KEY in environment variable first.')
        return None
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query})
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    result = json.loads(response.text)
    # 提取organic的title、link、snippet
    organic = [{'title': item['title'], 'link': item['link'], 'snippet': item['snippet']} for item in result['organic']]
    return organic