create table if not exists amazon_book_reviews (
    overall int not null,
    reviewText text not null,
    tfIdfText text,
    reviewerID text,
    reviewerName text,
    reviewDate date
)