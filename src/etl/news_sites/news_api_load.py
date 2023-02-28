import newsapi
import pandas as pd
import datetime
from requests_cache import CachedSession
from news_site_scraper import scrape_news_page

NEWS_SOURCES = "abc-news, fox-news, cnn, reuters, al-jazeera-english"
TABLE_NAME = "news_api"


def create_news_api_client():
    """
    Creates a client to [newsapi](https://newsapi.org/).

    Loads api-key from local file.
    """
    # Make sure all made requests are cached
    session = CachedSession()

    # get api newsapi api-key
    with open("../../newsapi.key", "r") as file:
        api_key = file.read()

    # Create and return client to the api
    return newsapi.NewsApiClient(
        api_key=api_key, 
        session=session    
    )
    

def get_all_news(query=None, time_from:datetime.date=None, time_to:datetime.date=None, page:int=None) -> str:
    """
    Search through all of [newsapi's](https://newsapi.org/) existing articles.

    ## Params:
    
    query: str, search-term
        find articles with titles and bodies matchin the query

    time_from: date
        find articles from this date

    time_from: date
        find articles up to this date
    """

    # Convert dates to iso-format, required by api
    if time_from:
        time_from = time_from.isoformat()
    
    if time_to:
        time_to = time_to.isoformat()

    # Create api client
    client = create_news_api_client()

    # Make request
    news_articles = client.get_everything(
        q=query,
        sources=NEWS_SOURCES,   #force sources
        language="en",          # force language
        from_param=time_from,
        to=time_to,
        page=page
    )

    return news_articles


def get_top_headlines_articles(query=None, category=None, page:int=None):

    client = create_news_api_client()

    news_articles = client.get_top_headlines(
        query,
        sources=NEWS_SOURCES,
        category=category,
        language="en",
        page_size=100,
        page=page
    )

    return news_articles


def fill_article_contents(raw_news_articles:str) -> None:
    """
    Fills articles contents with scraped full, article content, as news api only returns a maximum of 200 chars.

    ## Params:
    raw_news_articles:json-string
        must be unprocessed raw result from either `get_top_headlines_articles()` or `get_all_news()`

    Example usage:
        `fill_article_contents(get_all_news())`
    """

    session = CachedSession()

    for article in raw_news_articles["articles"]:
        article["content"] = scrape_news_page(article["url"], session)


def articles_to_df(raw_news_articles:str) -> pd.DataFrame:
    df = pd.DataFrame(raw_news_articles["articles"])
    df["source"] = df["source"].apply(lambda x: x["id"])
    del df["urlToImage"]

    df["publishedAt"] = pd.to_datetime(df["publishedAt"])

    return df


def df_to_sql(df, conn_or_engine):
    df.to_sql(
        TABLE_NAME,
        con=conn_or_engine,
        if_exists="append",
        index=False
    )