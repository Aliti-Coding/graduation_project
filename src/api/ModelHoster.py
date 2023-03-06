from flask import Flask, request
import json
from typing import Optional, Dict, List, Callable
from itertools import zip_longest

class ModelHoster:
    """
    Simple API interface to host models or even functions.
    """
    def __init__(
            self,
            models: List[Callable],
            models_schemas: Optional[List[Dict]] = [None]
        ) -> None:

        self.app = Flask(__name__)
        
        def predict(scma):
            if request.method == "GET":
                return scma
            elif request.method == "POST":
                if request.is_json:
                    inputs = json.loads(request.json)
                    print(inputs)
                    inputs = inputs[list(inputs.keys())[0]] 
                else:
                    return {
                        "error": "request must contain json", "example": {
                            "text": "text to predict"
                        }
                    }

                result = model(inputs)

                return {"result":result}

        for model, schema in zip_longest(models, models_schemas, fillvalue=None):
            @self.app.route(f"/{model.__name__}", methods=["POST", "GET"])
            def prediction():
                default_schema = {
                    "model_hoster": {
                        "POST": "Contains json",
                        "JSON": {"text": "text to predict"} 
                        }
                }

                return predict(schema if schema else default_schema)
            
        @self.app.route("/", methods=["GET"])
        def index():
            hosted_models = "\n".join([f"<li> {model.__name__} </li>" for model in models])
            return f"""
            <h1> ModelHoster </h1>
            Hosted Models:
            <ul> 
            {hosted_models}
            </ul>
            """
            
    
    def host(self):
        self.app.run(port=1234, debug=True)

if __name__ == "__main__":
    hoster = ModelHoster([str])
    hoster.host()