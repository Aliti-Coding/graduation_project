from wordcloud import WordCloud, ImageColorGenerator
import matplotlib.pyplot as plt 
import numpy as np
import pandas as pd
from PIL import Image

def word_cloud(clean_text, upload_filepath):
    """ returns a image with words
        REMEMBER! specify the format:
        my_image.png

    Args:
        clean_text (_str_): _description_
        upload_filepath (_str_): _write the file path were you want the picture_

    Returns:
        _file_: _description_
    """

    wc = WordCloud(
        background_color = 'white',
        height = 1080,
        width = 1920,
        # contour_width = 3,
        # min_font_size=3,
        margin = 2
    ).generate(clean_text)



    return wc.to_file(upload_filepath)


#eks how to use it:
#   word_cloud(clean_text, "movie_reviews_aws/my_image.png")