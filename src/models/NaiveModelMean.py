import pandas as pd
import numpy as np

class NaiveModelMean:
    def __init__(self):
        ...

    def fit(self, data_path):
        x = pd.read_csv(data_path, usecols=["overall"]).to_numpy()
        self.mean_value = x.mean()
    
    def call(self, x):
        return self.__call__(x)
    
    def predict(self, x):
        return self.__call__(x)
    
    def __call__(self, x):
        return np.full_like(x, self.mean_value)
