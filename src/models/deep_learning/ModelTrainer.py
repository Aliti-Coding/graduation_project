from keras import Model
from keras.callbacks import Callback, ModelCheckpoint, EarlyStopping
from keras.metrics import Metric, Accuracy
from keras.losses import Loss, MeanSquaredError, MeanAbsoluteError
from keras.optimizers import Optimizer, Adam
from typing import Optional, List, Union, Literal
from os import PathLike

from time import time

class ModelTrainer(Model):
    def __init__(
            self,
            model: Model,
            save_path: Optional[Union[str, PathLike]] = None
        ) -> None:
        
        super().__init__()

        self.model = model
        
        self.save_path = save_path
        self.is_fit = False

    def compile(
            self,
            optimizer: Optimizer = Adam(),
            loss: Loss = MeanSquaredError(),
            metrics: List[Metric] = MeanAbsoluteError(),
            **kwargs
        ) -> None:

        self.model.compile(
            optimizer = optimizer,
            loss = loss,
            metrics = metrics,
            **kwargs
        )
    
      
    def fit(
            self,
            x, 
            y,
            epochs,
            callbacks: Optional[Union[List[Callback], Literal["default"]]] = "default",
            validation_data: Optional[tuple] = None,
            batch_size: Optional[int] = None,
            **kwargs
        ) -> dict:

        callbacks = callbacks if callbacks != "default" else [
            ModelCheckpoint(
                f"../../ckpt/{self.model.name}/model",
                save_best_only=True,
                save_weights_only=False
            ),
            EarlyStopping(
                patience=5,
                restore_best_weights=True
            )
        ]

        self.train_start_time = time()
        self.history = self.model.fit(
            x=x,
            y=y,
            batch_size=batch_size,
            epochs=epochs,
            validation_data=validation_data,
            callbacks=callbacks,
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
            "metrics": metrics_value,
            "trainable_weights": self.model.trainable_weights,
            "fit_params": self.history.params,
            "train_time": self.train_end_time - self.train_start_time,
            "train_start_time": self.train_start_time,
            "train_end_time": self.train_end_time
        }
