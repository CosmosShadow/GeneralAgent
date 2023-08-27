# 工具集，code可以操作的东西

def google_search(query):
    # 返回一个可以被json.loads加载的字符串
    import requests
    import json
    import os
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query})
    SERPER_API_KEY = os.environ['SERPER_API_KEY']
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.text


def wikipedia_search(query):
    # 返回纯文本字符串
    import requests
    from bs4 import BeautifulSoup

    def get_page_obs(page):
        # find all paragraphs
        paragraphs = page.split("\n")
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        # find all sentence
        sentences = []
        for p in paragraphs:
            sentences += p.split('. ')
        sentences = [s.strip() + '.' for s in sentences if s.strip()]
        return ' '.join(sentences[:5])

    def clean_str(s):
        return s.replace("\xa0", " ").replace("\n", " ")

    entity = query.replace(" ", "+")
    search_url = f"https://en.wikipedia.org/w/index.php?search={entity}"
    response_text = requests.get(search_url).text
    soup = BeautifulSoup(response_text, features="html.parser")
    result_divs = soup.find_all("div", {"class": "mw-search-result-heading"})
    if result_divs:
        result_titles = [clean_str(div.get_text().strip()) for div in result_divs]
        obs = f"Could not find {query}. Similar: {result_titles[:5]}."
    else:
        page = [p.get_text().strip() for p in soup.find_all("p") + soup.find_all("ul")]
        if any("may refer to:" in p for p in page):
            obs = wikipedia_search("[" + query + "]")
        else:
            page_content = ""
            for p in page:
                if len(p.split(" ")) > 2:
                    page_content += ' ' + clean_str(p)
                    if not p.endswith("\n"):
                        page_content += "\n"
            obs = get_page_obs(page_content)
            if not obs:
                obs = None
    return obs

# send_message_fun(type, content)
# 发送消息的函数，参数为消息内容
# type: text、react、json
# 可以是markdown的文本、也可以是一块react的代码、json

class Tools():
    def __init__(self, send_message_fun):
        self.funs = {}
        self.funs['send_message'] = send_message_fun
        self.funs['google_search'] = google_search
        self.funs['wikipedia_search'] = wikipedia_search