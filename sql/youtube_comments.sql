create table if not exists youtube_comments (
    id int not null,
    publish_date date,
    comment_text text
)