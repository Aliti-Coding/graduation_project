import requests
import json
import pandas as pd
from requests_cache import CachedSession
from typing import Literal, Optional, List

class TrustPilotApi:
    """
    Interface to trustpilot api, through their front-end.

    All requests are cached.
    """

    def __init__(self) -> None:
        self._base_url = "https://www.trustpilot.com/_next/data/businessunitprofile-consumersite-7193/review/"
        self.session = CachedSession("trustpilot_api")
    
    def reviews(
            self,
            company_website: str,
            num_pages: int = 1,
            start_page: int = 1,
            clean_reviews: bool = True,
            sort: Optional[Literal["recency", "relevance"]] = None,
            date: Optional[Literal["last30days", "last3months", "last6months", "last12months"]] = None,
            stars: Optional[Literal[1, 2, 3, 4, 5]] = None 
        ) -> List[dict]:

        """
        Get reviews for `company_website` over multiple pages.
        """

        reviews = []
        
        for page in range(start_page, start_page+num_pages):
            if clean_reviews:
                reviews += self._clean_reviews(
                    self._fetch_reviews(
                        company_website,
                        page,
                        sort,
                        date,
                        stars
                    )
                )
            
            elif not clean_reviews:
                reviews.append(
                    self._fetch_reviews(
                        company_website,
                        page,
                        sort,
                        date,
                        stars
                    )
                )
        
        return reviews


    def _fetch_reviews(
            self,
            company_website,
            page,
            sort,
            date,
            stars
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
        

    def _clean_reviews(
            self,
            raw_reviews: List[dict]
        ) -> list:

        """
        Extracts review text, rating, title and creation date from TrustPilot reviews.

        See `get_reviews` to get much more data from reviews.
        """
        
        extracted_reviews = []

        reviews=raw_reviews["pageProps"]["reviews"]

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