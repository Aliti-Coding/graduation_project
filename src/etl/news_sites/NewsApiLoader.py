import newsapi
import pandas as pd
import datetime
from requests_cache import CachedSession
from typing import Optional

NEWS_SOURCES = "abc-news,fox-news,cnn,reuters,al-jazeera-english"


class NewsApiLoader:
    """
    NewsApiLoader class.

    Get articles from NewsAPI, articles are automatically converted to a pandas DataFrame and are stored in the instance through the `df` property.
    """

    def __init__(
            self,
            newsapi_key: str,
            news_sources: Optional[str] = None,
            source_language: str = "en"
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

        self.session = CachedSession("news_api_cache")
        
        self.newsapi_client = newsapi.NewsApiClient(
            api_key = newsapi_key,
            session=self.session
        )

        self.news_sources = news_sources

        self.source_language = source_language

        self.df = None


    def search_all_articles(
            self,
            query = None,
            time_from: Optional[datetime.date] = None,
            time_to: Optional[datetime.date] = None,
            page: Optional[int] = None,
            overwrite: bool = False,
        ) -> None:
        
        """
        Search through all of [newsapi's](https://newsapi.org/) existing articles.

        Results are stored or appended to existing instance df.

        Get the result through the classes `df` property.
        
        ## Parameters
        query: str, search-term,
            find articles with titles and bodies matchin the query

        time_from: date,
            find articles from this date

        time_from: date,
            find articles up to this date

        page: int,
            the n'th page to get articles from, use to crawl pages

        overwrite: bool,
            if True then replace existing DataFrame with articles when pulling new articles
        """

        # Convert dates to iso-format, required by api
        if time_from:
            time_from = time_from.isoformat()

        if time_to:
            time_to = time_to.isoformat()

        # Make request
        news_articles = self.newsapi_client.get_everything(
            q=query,
            sources=self.news_sources,
            language=self.source_language, 
            from_param=time_from,
            to=time_to,
            page=page
        )

        self.raw_articles_to_df(news_articles)
    
    def current_top_headlines(
            self,
            query: Optional[str] = None,
            category: Optional[str] = None,
            page: Optional[int] = None,
            page_size: int = 100,
            overwrite: bool = False,
        ) -> None:

        """
        Get the current top headlines of news sources.

        Use `query` to search for specific keywords across articles.
        
        ## Params:
        overwrite: bool,
            if True then replace existing DataFrame with articles when pulling new articles
        """

        news_articles = self.newsapi_client.get_top_headlines(
            query,
            sources=self.news_sources,
            category=category,
            language=self.source_language,
            page_size=page_size,
            page=page
        )

        self.raw_articles_to_df(
            news_articles, 
            overwrite=overwrite
        )
    
    def raw_articles_to_df(
            self, 
            raw_news_articles: str,
            overwrite: bool = False,
        ) -> None:

        """
        Converts raw output of NewsAPI responses to a dataframe.
        """

        temp_df = pd.DataFrame(raw_news_articles["articles"])

        # Extract the name of news provider as source
        temp_df["source"] = temp_df["source"].apply(lambda x: x["id"])

        # Del unneeded column
        del temp_df["urlToImage"]

        temp_df["publishedAt"] = pd.to_datetime(temp_df["publishedAt"])

        # Check if a dataframe already exists in class instance
        # It does not exist, create new df property
        if not self.__dict__.get("df", None):
            self.df = temp_df
        
        else:    
            # Replace existing df with new one
            if overwrite:
                self.df = temp_df
            
            # Concat existing and new dataframe
            elif not overwrite:
                pd.concat([self.df, temp_df])

    def clear_df(self) -> None:
        """
        Completely clear df containing news articles
        """

        del self.df
        self.df = None