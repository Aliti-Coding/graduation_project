from newsapi import NewsApiClient
import pandas as pd
import datetime
from requests_cache import CachedSession
from typing import Optional

NEWS_SOURCES = "abc-news,fox-news,cnn,reuters,al-jazeera-english"


class NewsApiLoader(NewsApiClient):
    """
    NewsApiLoader class.

    Get articles from NewsAPI, articles are automatically converted to a pandas DataFrame.
    """ 

    def __init__(
            self,
            api_key: str,
            sources: Optional[str] = None,
            source_language: Optional[str] = "en",
        ) -> None:

        """
        ## Parameters
        newsapi_key: str, api-key,
            your api-key to NewsAPI.

        news_sources: str, optional,
            a string of news sources to get articles from seperated by ','. Ex. "abc-news, fox-news, cnn".
        
        source_language:str, iso-format,
            iso-format language string, get articles in specified language.
    
        """

        super().__init__(
            api_key=api_key,
            session=CachedSession("news_api_cache")
        )
        
        self.sources = sources

        self.source_language = source_language


    def get_everything(
            self,
            page: Optional[int] = 1,
            pages: Optional[int] = 1,
            page_size: Optional[int] = 100,
            **kwargs

         ) -> pd.DataFrame:
        
        f"""
        {NewsApiClient.get_everything.__doc__}
        """

        raw_articles = []
        for p in range(page, pages + page if pages else 1 + page):
            raw_articles += super().get_everything(
                page=p,
                page_size=page_size,
                sources=self.sources
                **kwargs
            )["articles"]
        
        return self._raw_articles_to_df(raw_articles)


    def get_top_headlines(
            self,
            page: Optional[int] = 1,
            pages: Optional[int] = 1,
            page_size: Optional[int] = 100,
            **kwargs
        ) -> None:

        f"""
        {NewsApiClient.get_top_headlines.__doc__}
        """

        raw_articles = []
        for p in range(page, pages + page if pages else 1 + page):
            raw_articles += super().get_top_headlines(
                page=p,
                page_size=page_size,
                sources=self.sources
                **kwargs
            )["articles"]
        
        return self._raw_articles_to_df(raw_articles)
    

    def _raw_articles_to_df(
            self, 
            raw_news_articles: str,
            overwrite: bool = False,
        ) -> None:

        """
        Converts raw output of NewsAPI responses to a dataframe.
        """

        df = pd.DataFrame(raw_news_articles)

        # Extract the name of news provider as source
        df["source"] = df["source"].apply(lambda x: x["id"])

        # Del unneeded column
        del df["urlToImage"]

        df["publishedAt"] = pd.to_datetime(df["publishedAt"])

        return df