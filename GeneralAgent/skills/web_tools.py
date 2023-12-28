def google_search(query: str) -> str:
    """
    google search with query, return a result in string
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
    result = json.dumps([{'title': item['title'], 'link': item['link'], 'snippet': item['snippet']} for item in result['organic']])
    # print(result)
    from GeneralAgent import skills
    messages = [
        {'role': 'system', 'content': f'background: {result[:30000]}'},
        {'role': 'user', 'content': f'{query}'},
    ]
    result = skills.llm_inference(messages)
    return result
    


def scrape_web(url, keep_url=False) -> str:
    """
    scrape static and dynamic content from a web page, and return the text content with markdown links
    @param url: url of the web page
    @return: text content of the web page
    """
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    from bs4 import BeautifulSoup
    import time
    import re
    from urllib.parse import urljoin

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

    # Wait for the dynamic content to load
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

    # Scroll down the page to trigger potential Ajax requests
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to the bottom of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait for new content to load
        time.sleep(3)
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Additional wait if necessary
    time.sleep(5)

    html = driver.page_source
    driver.quit()

    # Parse html content
    soup = BeautifulSoup(html, "html.parser")
    # print(soup.get_text())
    # print(soup.prettify())
    for span in soup.find_all("span"):
        span.replace_with(span.text)
    for a in soup.find_all("a"):
        if keep_url:
            href = urljoin(url, a.get('href'))
            a.replace_with(f"[{a.text}]({href})")
        else:
            a.replace_with(f"[{a.text}]()")
    for br in soup.find_all("br"):
        br.replace_with("\n")
    text = soup.get_text(separator="\n")

    # Replace multiple newlines and spaces around them with a single newline
    text = re.sub('\s*\n\s*', '\n', text)

    # Collapse whitespace
    text = ' '.join(text.split())

    return text


def test_scrape_web():
    """
    This function tests the scrape_web function.
    It asserts that the returned text contains the string 'replicate'.
    """
    url = "https://replicate.com/stability-ai/stable-video-diffusion/api?tab=python"
    text = scrape_web(url)
    assert 'replicate' in text
    print(text)


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


if __name__ == '__main__':
    result = google_search('成都 人口')
    print(result)