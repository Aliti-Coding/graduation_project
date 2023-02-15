create table if not exists news_api (
    id serial primary key,
    source text,
    author text,
    title text,
    description text,
    url text,
    publishedAt date,
    content text
)