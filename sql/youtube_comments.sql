create table if not exists youtube_comments (
    id SERIAL PRIMARY KEY,
    publish_date date,
    comment_text text
)