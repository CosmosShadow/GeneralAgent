def scrape_dynamic_web(url):
    """
    This function takes a url and returns the text content of the web page.
    It uses selenium to load the dynamic content of the page, and BeautifulSoup to parse the HTML and extract the text.
    It also replaces <span> tags with their text content, and <br> tags with newline characters.
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
    chrome_options.add_argument("--headless") # Ensure GUI is off
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Set path to chromedriver as per your configuration
    webdriver_service = Service(ChromeDriverManager().install())

    # Choose Chrome Browser
    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
    driver.get(url)

    # Wait for the dynamic content to load
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

    html = driver.page_source
    driver.quit()

    # Parse html content
    soup = BeautifulSoup(html, "html.parser")
    for span in soup.find_all("span"):
        span.replace_with(span.text)
    for a in soup.find_all("a"):
        href = urljoin(url, a.get('href'))
        a.replace_with(f"[{a.text}]({href})")
    for br in soup.find_all("br"):
        br.replace_with("\n")
    text = soup.get_text(separator="\n")

    # Replace multiple newlines and spaces around them with a single newline
    text = re.sub('\s*\n\s*', '\n', text)

    # Collapse whitespace
    text = ' '.join(text.split())

    return text

def test_scrape_dynamic_web():
    """
    This function tests the scrape_dynamic_web function.
    It asserts that the returned text contains the string 'replicate'.
    """
    url = "https://replicate.com/stability-ai/stable-video-diffusion/api?tab=python"
    text = scrape_dynamic_web(url)
    assert 'replicate' in text
    print(text)

if __name__ == '__main__':
    test_scrape_dynamic_web()