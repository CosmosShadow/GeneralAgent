def scrape_web(url: str):
    """
    Scrape web page, return (title: str, text: str, image_urls: [str], hyperlinks: [str]) when success, otherwise return None.
    """
    # TODO: use selenium
    import re
    import requests
    from bs4 import BeautifulSoup
    from requests.compat import urljoin
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        title = str(soup.title.string)
        text = str(re.sub(r'<style.*?</style>', '', soup.get_text(), flags=re.DOTALL))
        image_urls = [str(image['src']) for image in soup.find_all('img')]
        hyperlinks = [(str(link.text), str(urljoin(url, link["href"]))) for link in soup.find_all("a", href=True) if urljoin(url, link["href"]).startswith('http')]
        return (title, text, image_urls, hyperlinks)
    except Exception as e:
        import logging
        logging.exception(e)
    return None