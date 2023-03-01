import requests
import json
import pandas as pd
from requests_cache import CachedSession


class TrustPilotApi:
    """
    Interface to trustpilot api, through their front-end.

    All requests are cached.
    """

    def __init__(self) -> None:
        self._base_url = "https://www.trustpilot.com/_next/data/businessunitprofile-consumersite-7193/review/"
        self.session = CachedSession("trustpilot_api")
    
        
    def get_reviews(
            self,
            company_website:str,
            page:int=1,
            sort:str="recency",
            date:str="",
            stars:str="",
        ) -> dict:
        """
        Get reviews for `company_website` ie. 'www.teslamotors.com'.

        Response contains tons of information, see `get_clean_reviews` to get only relevant content.
        ## Params:
        page: int,
            pagenumber of reviews.

        sort: str,
            sorting method of reviews.
        
        date: str, iso-format,
            Date to get reviews for.??

        stars: str,
            which stars/rating the resulting reviews have.????
        """
        
        target_url = f"{self._base_url}{company_website}.json?sort={sort}"

        if page > 1:
            target_url+=f"&page={page}"
        
        if date:
            target_url+=f"&date={date}"
        
        if stars:
            target_url+=f"&stars={stars}"

        resp = self.session.get(target_url)

        if not resp.ok:
            raise requests.HTTPError(resp)
        
        else:
            return resp.json()
        

    def get_clean_reviews(
            self,
            company_website:str,
            page:int=1,
            sort:str="recency",
            date:str="",
            stars:str="",
        ) -> list:

        """
        Extracts review text, rating, title and creation date from TrustPilo reviews.

        See `get_reviews` to get much more data from reviews.
        """
        
        raw_reviews_json = self.get_reviews(
            company_website,
            page,
            sort,
            date,
            stars
        )

        extracted_reviews = []

        reviews=raw_reviews_json["pageProps"]["reviews"]

        for review in reviews:
            extracted_reviews.append(
                {
                    "text": review["text"] if review["text"] else "",
                    "rating": review["rating"] if review["rating"] else None,
                    "title": review["title"] if review["title"] else "",
                    "creation_date": review["dates"]["publishedDate"] if review["dates"]["publishedDate"] else None
                }
            )

        return extracted_reviews