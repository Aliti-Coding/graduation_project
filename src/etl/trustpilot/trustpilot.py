import requests
import json
import pandas as pd


def get_reviews(company_website, num_pages=1, start_page=1):
    """
    Extracts and transforms TrustPilot reviews for `company_website` over `num_pages` starting from page number `start_page`.
    """
    reviews = []

    for page in range(start_page, start_page+num_pages):
        
        raw_review = get_review_data(
            company_website, 
            page=page
        )

        clean_reviews = extract_reviews_data(raw_review)
        
        reviews += clean_reviews
    
    return reviews


def get_review_data(
    company_website:str, 
    page:int=1,
    sort:str="recency",
    date="",
    stars="",
):

    """
    Returns TrustPilot json data of reviews for a `company_website` from page number `page`.
    """

    BASE_URL = "https://www.trustpilot.com/_next/data/businessunitprofile-consumersite-7193/review/"

    # Construct the final url to be used to query the trustpilot API
    target_url = BASE_URL + company_website + f".json?sort={sort}"
    
    if page > 1:
        target_url+=f"&page={page}"
        
    if date:
        target_url+=f"&date={date}"
    
    if stars:
        target_url+=f"&stars={stars}"


    resp = requests.get(target_url)

    if not resp.ok:
        print(f"WARNING: something went wrong making requests, status code: {resp.status_code}, url:{resp.url}")
    
    else:
        return resp.json()


def extract_reviews_data(raw_reviews):
    """
    Extracts relevant data from list of json reviews from TrustPilot (`get_review_data`)
    """

    extracted = []
    try:
        reviews=raw_reviews["pageProps"]["reviews"]
    
    
        for review in reviews:
            text = review["text"] if review["text"] else ""
            rating = review["rating"] if review["rating"] else None
            title = review["title"] if review["title"] else ""
            rating = review["rating"] if review["rating"] else None
            creation_date = review["dates"]["publishedDate"] if review["dates"]["publishedDate"] else None

            clean_review = {
                "text":text,
                "rating":rating,
                "title":title,
                "creation_date":creation_date
            }

            extracted.append(clean_review)
    except Exception as e:
        print(e)
    
    return extracted