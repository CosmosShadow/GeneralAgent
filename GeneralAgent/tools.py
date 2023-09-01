# 工具集，code可以操作的东西
import json
import os
import requests
from bs4 import BeautifulSoup
from requests.compat import urljoin
from playwright.sync_api import sync_playwright
from GeneralAgent.keys import SERPER_API_KEY

def google_search(query):
    """
    google search with query, return a result in dict.
    return:
    {
        "knowledgeGraph": {"title": "", "type": "", "website": "", "imageUrl": "", "description": "", "descriptionSource": "", "descriptionLink": "", "attributes": {"x": "x"}},
        "organic": [{"title": "", "link": "", "snippet": "", "sitelinks": [{"title": "","link": ""}],"position": 1},{"title": "x", "link": "x", "snippet": "x","position": 2}],
        "peopleAlsoAsk": [{"question": "","snippet": "","title": "","link": ""}],
        "relatedSearches": [{"query": ""}]
    }
    """
    # 返回一个可以被json.loads加载的字符串
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query})
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


def scrape_web(url: str) -> str:
    """Scrape page title, content(string) and links([(text, link)]) from a webpage url"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        try:
            page.goto(url)
            html_content = page.content()
            soup = BeautifulSoup(html_content, "html.parser")

            # for script in soup(["script", "style"]):
            #     script.extract()
            # text = soup.get_text()
            # lines = (line.strip() for line in text.splitlines())
            # chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # text = "\n".join(chunk for chunk in chunks if chunk)

            # # 剔除掉文本中 <style xxx > xxx </style> 中所有内容
            # import re
            # text = re.sub(r'<style.*?</style>', '', text, flags=re.DOTALL)

            title = page.title()
            text = page.evaluate('document.body.innerText')
            # text = page.evaluate('document.body.textContent')

            # hyperlinks: [(text (link))]
            hyperlinks = [(link.text, urljoin(url, link["href"])) for link in soup.find_all("a", href=True)]
            hyperlinks = [(text, link) for (text, link) in hyperlinks if link.startswith('http')]

        except Exception as e:
            title = None
            text = f"Error: {str(e)}"
            hyperlinks = []
        finally:
            browser.close()

    return title, text, hyperlinks


# send_message_fun(type, content)
# 发送消息的函数，参数为消息内容
# type: text、react、json
# 可以是markdown的文本、也可以是一块react的代码、json

class Tools():
    def __init__(self):
        self.funs = []

    def add_funs(self, funs):
        self.funs += funs

    def get_funs_description(self):
        return [f.__doc__ for f in self.funs]