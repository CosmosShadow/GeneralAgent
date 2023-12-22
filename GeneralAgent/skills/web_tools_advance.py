# advance web tools

def web_open(url: str):
    """
    open a web page in browser and wait the page load completely, return the Selenium 4 driver. 
    use driver.find_element to find the element in the page.
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
    import time

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

    # Additional wait if necessary
    time.sleep(5)

    # html = web_get_html(driver)
    # print(f'driver of web ({url}) is ready. the html content of driver is below:```\n{html}\n```')

    return driver


def web_get_html(driver) -> str:
    """
    return html content of the Selenium 4 driver
    """
    from bs4 import BeautifulSoup, Comment
    html = driver.page_source

    soup = BeautifulSoup(html, 'html.parser')

    # Remove script and style elements
    for script_or_style in soup(['script', 'style']):
        script_or_style.decompose()  # Remove the tag from the soup

    # Remove comments
    for comment in soup(text=lambda text: isinstance(text, Comment)):
        comment.extract()

    # Convert the soup back to a string
    cleaned_html = str(soup)

    # print(cleaned_html)

    return cleaned_html





if __name__ == '__main__':
    pass