from flask import Flask
from connect_db import connect_to_grad_db
from create_news_article import *

from sqlalchemy import TextClause

app = Flask(__name__)

engine = connect_to_grad_db()

def create_homepage():
    with engine.connect() as conn:
        stmt = TextClause("SELECT news_api_id, title, source, mean_preds FROM news_api_w_preds limit 10;")
        articles = conn.execute(stmt).fetchall()

    document = """<!DOCTYPE html>
<h1>Select Article to View</h1>
"""
    document += "<ul>\n"

    for article in articles:
        document += f"<li><a href=/article/{article[0]}>{article[1]} - {article[2]}</a> <b>[{article[3]}]</b></li>\n"
    
    return document
    
@app.route("/")
def index():
    return create_homepage()

@app.route("/article/<article_id>")
def load_article(article_id):
    with engine.connect() as conn:
        return create_news_article(article_id, conn)
    

if __name__ == "__main__":
    app.run(port=8080, debug=True) 