from keras import Model
from keras.callbacks import Callback, ModelCheckpoint, EarlyStopping
from keras.metrics import Metric, Accuracy
from keras.losses import Loss, MeanSquaredError, MeanAbsoluteError
from keras.optimizers import Optimizer, Adam
from typing import Optional, List, Union, Literal
from os import PathLike

from time import time

class ModelTrainer:
    def __init__(
            self,
            model: Model,
            optimizer: Optimizer = Adam(),
            loss: Loss = MeanSquaredError(),
            metrics: List[Metric] = MeanAbsoluteError(),
            callbacks: Union[List[Callback], Literal["default"]] = "default",
            save_path: Optional[Union[str, PathLike]] = None
        ) -> None:
        

        self.is_fit = False

        self.model = model
        self.optimizer = optimizer
        self.loss = loss
        self.metrics = metrics if metrics else Accuracy()
        
        self.callbacks = callbacks if callbacks != "default" else [
            ModelCheckpoint(
                "../../checkpoints/2d_cnn_32_16_32_250k/model",
                save_best_only=True,
                save_weights_only=False
            ),
            EarlyStopping(
                patience=5,
                restore_best_weights=True
            )
        ]

        self.save_path = save_path

    def compile(self, **kwargs) -> None:
        self.model.compile(
            optimizer = self.optimizer,
            loss = self.loss,
            metrics = self.metrics,
            **kwargs
        )
    
      
    def fit(
            self,
            x, 
            y,
            batch_size,
            epochs,
            vaiidation_data: tuple,
            **kwargs
            
        ) -> dict:

        self.train_start_time = time()
        self.history = self.model.fit(
            x=x,
            y=y,
            batch_size=batch_size,
            epochs=epochs,
            validation_data=vaiidation_data,
            callbacks=self.callbacks
            **kwargs
        )

        self.train_end_time = time()
        self.is_fit = True

        return self.history
    

    def stats(
            self, 
            y_true, 
            y_pred, 
            loss: Optional[Loss] = None, 
            metrics: Optional[List[Metric]] = None
        ) -> dict:

        if not loss:
            loss_value = {
                self.loss.name: self.loss.call(y_true, y_pred).numpy()
            }
        elif loss:
            loss_value = {
                loss.name: loss.call(y_true, y_pred.numpy())
            }

        if not metrics:
            metrics_value = {
                m.name: m.call(y_true, y_pred) for m in self.metrics.numpy()
            }        
        
        elif metrics:
            metrics_value = {
                m.name: m.call(y_true, y_pred) for m in metrics.numpy()
            }
        
        
        return {
            "model_name": self.model.name,
            "loss": loss_value,
            "metrics": metrics,
            "trainable_weights": self.model.trainable_weights,
            "fit_params": self.history.params,
            "train_time": self.train_end_time - self.train_start_time,
            "train_start_time": self.train_start_time,
            "train_end_time": self.train_end_time
        }
