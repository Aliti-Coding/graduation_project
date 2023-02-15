import sys

sys.path.insert(1, r"..\models")
sys.path.insert(2, r"..\etl")

from lstm_model import load_model_weights_from_checkpoint
from connect_db import connect_to_grad_db


model=load_model_weights_from_checkpoint()

model.predict(["i hate this"])


