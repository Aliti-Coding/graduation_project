import pandas as pd
import re
import math
from sqlalchemy import select, column, table, TextClause

from connect_db import connect_to_grad_db


banners = {
    "fox-news":"https://s1.qwant.com/thumbr/0x380/9/6/9484111a9e2eb4cbb8ede5d0bc606c378ed898aeb7f1bd2dd64a13b79b7d16/1200px-Fox_News_Channel_logo.svg.png?u=https%3A%2F%2Fupload.wikimedia.org%2Fwikipedia%2Fcommons%2Fthumb%2F6%2F67%2FFox_News_Channel_logo.svg%2F1200px-Fox_News_Channel_logo.svg.png&q=0&b=1&p=0&a=0",
    "abc-news":"https://s1.qwant.com/thumbr/700x0/3/e/0247f90b2a3859f30c2f2aa3bf8c0a4a3bb5fb50a4356a0fabc82cb6a014b6/latest.jpg?u=https%3A%2F%2Fvignette4.wikia.nocookie.net%2Flogopedia%2Fimages%2Fe%2Fe1%2FABC_News.jpg%2Frevision%2Flatest%3Fcb%3D20151013161111&q=0&b=1&p=0&a=0",
    "cnn":"https://s2.qwant.com/thumbr/700x0/f/e/fb9962b40abff59c434b2e63eb63d72021cb7912e6f784bd2388fd21ff67c4/cnn-logo-1-1.png?u=https%3A%2F%2Flogodownload.org%2Fwp-content%2Fuploads%2F2014%2F11%2Fcnn-logo-1-1.png&q=0&b=1&p=0&a=0",
    "al-jazeera-english":"https://s2.qwant.com/thumbr/0x380/6/e/8509f372409f486f2279183019365bd9b0599d3b4c01dd6829861561e0e77e/JAZEERA-LOGO.jpg?u=http%3A%2F%2Fwww.wired.com%2Fwp-content%2Fuploads%2Fimages_blogs%2Fbusiness%2F2011%2F01%2FJAZEERA-LOGO.jpg&q=0&b=1&p=0&a=0"
}

def decimal_to_rbg(decimal):
    r = int((4-decimal)*255/4)
    g = int((decimal)*255/4)
    b = 120


    return f"rgb({r}, {g}, {b})"


def create_news_article(id, conn):
    stmt = TextClause(f"SELECT * FROM news_api_w_preds WHERE news_api_id = {id} limit 1;")
    article_data = conn.execute(stmt).fetchone()


    text_w_preds = article_data[10]
    sentences = re.split(r"\. ", text_w_preds)

    html_sentences = []
    for sentence in sentences:
        pred = float(re.search(r"\[\[(.*)\]\]", sentence).group(1))

        pred_color = decimal_to_rbg(pred)
        html_text = fr'<div style="background-color:{pred_color};"><t>{sentence}.</t></div>'

        html_sentences.append(html_text)

    title = article_data[3]
    title = f"<h1>{title}</h1>"

    date= article_data[6]
    date = f"<p>Published: {date}</p>"

    author = article_data[2]
    author = f"<p>Written by: {author}</p>"

    mean_pred = article_data[9]
    mean_pred = f"<b style='background-color:{decimal_to_rbg(mean_pred)};padding:0px;'>{mean_pred}</b>"

    source = article_data[1]
    banner = f"<img src='{banners[source]}' style='height:100px;'>"

    tfidf = f"<p>TF-IDF: <b>{', '.join(article_data[11:15])}</b></p>"

    document = "<!DOCTYPE html>\n"
    document += "<html>\n"
    document += f"{banner}\n"
    document += f"{title}\n"
    document += f"<p>Source: {source}</p>\n"
    document += f"{date}\n"
    document += f"{author}\n"
    document += f"{tfidf}\n"
    document += f"Sentiment overall [0-4]: <br>{mean_pred}<br><br>\n"
    document += f"<a href=/article/{article_data[8]-1}>Prev Article</a> | <a href=/article/{article_data[8]+1}>Next Article</a>"
    document += (
"""
<style>

    t {
        font-size: large;
        line-height: ;
        padding:10px;
        width:auto;
    }

    div {
        padding:10px;
        border-radius:10px;
        margin:10px;
    }

    article {
        border-radius:10px;
    }

    html {
        margin:0 450px;
        text-align: center;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    }
</style>
""")
    document += "<article>\n"
    document += f"{''.join(html_sentences)}\n"
    document += "</article>\n"
    document += f"</html>"

    return document