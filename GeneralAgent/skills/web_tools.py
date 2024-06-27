def google_search(query: str) -> str:
    """
    google search with query, return a result in string
    """
    import os
    import json
    import requests
    SERPER_API_KEY = os.environ.get('SERPER_API_KEY', None)
    if SERPER_API_KEY is None:
        raise Exception('Please set SERPER_API_KEY in environment variable first.')
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query})
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    json_data = json.loads(response.text)
    return json.dumps(json_data, ensure_ascii=True, indent=4)


def web_search(query: str) -> str:
    """
    网页搜索
    """
    return google_search(query)


def wikipedia_search(query: str) -> str:
    """
    wikipedia search with query, return a result in string
    """
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


def _web_driver_open(url: str, wait_time=10, scroll_to_bottom=False):
    """
    open a web page in browser and wait the page load completely, return the Selenium 4 driver.
    @param url: the url of the web page
    @param wait_time: the time to wait for the page to load completely
    @param scroll_to_bottom: whether to scroll to the bottom of the page to trigger potential Ajax requests
    """
    import os
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.options import Options
    import time

    # 开发环境使用本地chrome浏览器，生产环境使用远程chrome浏览器
    CHROME_GRID_URL = os.environ.get('CHROME_GRID_URL', None)
    if CHROME_GRID_URL is not None:
        chrome_options = Options()
        driver = webdriver.Remote(command_executor=CHROME_GRID_URL, options=chrome_options)
    else:
        # Setup chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Ensure GUI is off
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        # Set a common user agent to mimic a real user
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36")
        # Set path to chromedriver as per your configuration
        webdriver_service = Service(ChromeDriverManager().install())
        # Choose Chrome Browser
        driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

    driver.get(url)
    driver.implicitly_wait(wait_time)
    if scroll_to_bottom:
            # Scroll down the page to trigger potential Ajax requests
        last_height = driver.execute_script("return document.body.scrollHeight")
        for _ in range(2):
            # Scroll down to the bottom of the page
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait for new content to load
            time.sleep(3)
            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
    return driver


def _web_driver_get_html(driver) -> str:
    """
    return clear html content (without scirpt, style and comment) of the Selenium 4 driver, the driver should be ready.
    """
    # 通过driver获取网页地址
    from bs4 import BeautifulSoup, Comment
    from urllib.parse import urljoin
    url = driver.current_url
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    # 移除script和style
    for script_or_style in soup(['script', 'style']):
        script_or_style.decompose()  # Remove the tag from the soup
    # 移除注释
    for comment in soup(text=lambda text: isinstance(text, Comment)):
        comment.extract()
    # 移除不必要的标签和属性、id
    for tag in soup(['head', 'meta', 'link', 'title', 'noscript', 'iframe', 'svg', 'canvas', 'audio', 'video', 'embed', 'object', 'param', 'source', 'track', 'map', 'area', 'base', 'basefont', 'bdi', 'bdo', 'br', 'col', 'colgroup', 'datalist', 'details', 'dialog', 'hr', 'img', 'input', 'keygen', 'label', 'legend', 'meter', 'optgroup', 'option', 'output', 'progress', 'select', 'textarea', 'script', 'style', 'comment']):
        tag.decompose()
    # 所有div、span标签的属性全部清空
    for tag in soup(['div', 'span']):
        tag.attrs = {}
    # 补全href地址
    for a in soup.find_all('a', href=True):
        a['href'] = urljoin(url, a['href'])
    # 补全图片
    for img in soup.find_all('img', src=True):
        img['src'] = urljoin(url, img['src'])
    # 返回内容
    html = str(soup)
    return html


def web_get_html(url:str, wait_time=10, scroll_to_bottom=True):
    """
    获取网页的html内容(不包含script, style和comment)
    @param url: the url of the web page
    @param wait_time: the time to wait for the page to load completely
    @param scroll_to_bottom: whether to scroll to the bottom of the page to trigger potential Ajax requests
    """
    import logging
    driver = None
    try:
        driver = _web_driver_open(url, wait_time, scroll_to_bottom)
        html = _web_driver_get_html(driver)
        return html
    except Exception as e:
        logging.exception(e)
        return 'Some Error Occurs:\n' + str(e)
    finally:
        if driver is not None:
            driver.quit()


def web_get_text(url:str, wait_time=10, scroll_to_bottom=True):
    """
    获取网页的文本内容
    @param url: the url of the web page
    @param wait_time: the time to wait for the page to load completely
    @param scroll_to_bottom: whether to scroll to the bottom of the page to trigger potential Ajax requests
    """
    import logging
    driver = None
    try:
        driver = _web_driver_open(url, wait_time, scroll_to_bottom)
        # 'WebDriver' object has no attribute 'find_element_by_tag_name'
        # text = driver.find_element_by_tag_name('body').text
        text = driver.execute_script("return document.body.innerText")
        return text
    except Exception as e:
        logging.exception(e)
        return 'Some Error Occurs:\n' + str(e)
    finally:
        if driver is not None:
            driver.quit()


if __name__ == '__main__':
    result = google_search('成都 人口')