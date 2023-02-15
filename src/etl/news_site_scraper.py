import requests
from bs4 import BeautifulSoup
from requests_cache import CachedSession

def scrape_news_page(url, session:CachedSession) -> str:
    
    # Create soup from page content
    soup = BeautifulSoup(
        get_page_content(url, session), 
        features="html.parser"
    )

    # Aljazeera is completly missing article tag on articles
    if "aljazeera" in url:
        article = (soup.find("main") 
            .find("div", "wysiwyg wysiwyg--all-content css-ibbk12")
        )

        return article.text if article else ""
    
    # Find article in text
    article = soup.find("article")
    
    # Foxnews has different article setup than other sites
    if "foxnews" in url:
        article = article.find("div", "article-body")
    

    return article.text if article else ""


def get_page_content(url, session:CachedSession):
    resp = session.get(url)
    assert resp.ok

    return resp.content