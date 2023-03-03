import requests
from bs4 import BeautifulSoup
from requests_cache import CachedSession
from typing import Union

class NewsSiteScraper:
    def __init__(self) -> None:
        
        self.session = CachedSession("scraped_news_sites")

    def scrape_site(self, url:str):
        
        # Create soup from page content
        soup = BeautifulSoup(
            self._get_page_content(url), 
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
        if "foxnews" in url and article:
            article = article.find("div", "article-body")
        

        return article.text if article else ""


    def _get_page_content(self,url):
        resp = self.session.get(url)
        
        if not resp.ok:
            
            print(resp.content)
            
            raise Exception(f"Error getting content from url: {resp.url}, code: {resp.status_code}")

        return resp.content