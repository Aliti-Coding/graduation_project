import sys
sys.path.append(r"C:\Users\fehmm\OneDrive\Skrivebord\python\graduation_project")


import pandas as pd
#select table from database youtube comments
#use the predifined functions to make predictions on the comments
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String

from keras import layers
from keras.layers import TextVectorization
import tensorflow as tf

from models.neural_networks.lstm_model import create_lstm_model
from models.tf_idf.tfidf_functions import clean_data_df_youtube
print("Post-import")
import os
import json

with open("azure_pg_database_connection.key", "r") as file:
    conn_string = file.read()
    conn_string = "postgresql" + conn_string
    
engine = create_engine(fr"{conn_string}")


df = pd.read_sql('youtube_comments', con=engine)




def load_model_weights_from_checkpoint(model:keras.Model=None) -> keras.Model:
    """
    Example:
        >>> model = load_model_weights_from_checkpoint()
        >>> model.predict(["bad"])
    """

    # Create model if model not explicitly provided
    if not model:
        model = create_lstm_model()
    
    model.load_weights(r"C:\Users\fehmm\Brights\Alexander Haugerud - Graduation Project\saved_models\lstm_model_24_24_250k_rows")

    return model


model = load_model_weights_from_checkpoint()

# Get the current working directory
current_directory = os.getcwd()
print(f"Current directory: {current_directory}")


df_clean = clean_data_df_youtube(df)

