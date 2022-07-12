## Implement and Evaluate Your Own Model

To implement your model, you should inherit `BaseModel` defined in `models/base_model.py`. Here's an example:

```
class MyModel(BaseModel):
    @staticmethod
    def add_arguments(parser):
        # add model-specific arguments here
        ...
    
    def __init__(self, *args):
        # initialize your model here
        ...
        
    def forward(self, vic_frame, filt, *args):
        # implement the forwarding function here
        ...
```
Then, you should name your model and add it to `SUPPORTED_MODELS` in `models/__init__.py`. In this way, you can simply run your model by specifying `--model` argument in `eval.py`. 

You can also implement your own training and evaluating framework. However, we recommend using our `Evaluator()` in `v2x_utils/eval_utils.py` and `Channel()` in `models/model_utils/channel.py` to measure the average precision and 
average transmission cost of your model in vehicle-infrastructure cooperative detection.

- **Evaluator**: Construct a evaluator by `evaluator=Evaluator(pred_cls)`, where pred\_cls is a list of the prediction classes you want to evaluate on.Then, make sure the format of model prediction is the same as ground truth labels ,which is {"boxes_3d": ..., "labels_3d": ..., "scores_3d": ...}. Then, call `evaluator.add_frame(pred, label)`to add the results of a single frame. When finished with all the frames, simply call `evaluator.print_ap("3d"/"bev")` to get the average percision results under 3d/bev view.
- **Channel**: Construct a channel in your model by `self.channel=Channel()`. Then, every time you want to transfer information from infrastructure to vehicle in your model, call `self.channel.send(key, value)` and `value=self.channel.receive(key)`.  Remember to use `self.channel.flush()` to clear all cached data in the channel after processing a single frame (otherwise the AB results will be incorrect). Use `self.channel.average_bytes()` to get the average transmission cost.
