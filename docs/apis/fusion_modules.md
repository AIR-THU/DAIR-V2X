## Fusion Modules
We provide useful tools like file io, fusion modules, computational geometry, etc, which may help model design and implementation.

### Transmission Channel
There exists transmission cost from infrastructure to vehicle, and the number of bits transferred is an important metric to evalute the fusion model. Therefore, we provide `channel = Channel()`, a dictionary-format data structure to simulate the transmission process. When implementing your fusion model, modules that take `inf_frame` as input should **NOT** directly transmit any intermediate value. Instead, it must call `channel.send(key, value)` to transmit data. Since the channel is a shared object between different modules, the fusion model can acquire these values via `channel.receive(key)`. When the prediction is finished, `channel.flush()`should be called to clear the table. The module will automatically compute the actual bits of the value, and you can easily compute average transmission cost by `channel.average_bits()`. 
An example is shown below:

```
from fusion_modules import Channel

class InfModule(nn.Module):
    def __init__(self, channel):
        self.channel = channel
        self.layer1 = ...
        self.layer2 = ...
    
    def forward(self, inf_frame):
        # This function should NOT be called during VIC3D training or evaluation
        h = self.layer1(inf_frame)
        h = self.layer2(h)
        return h
        
    def trans_feats(self, inf_frame):
        h = self.layer1(inf_frame)
        self.pipe.send("feat1", h)
        h = self.layer2(h)
        self.pipe.send("feat2", h)
        
class FusionModel(nn.Module):
    def __init__(self, channel):
        self.channel = channel
        self.inf_module = InfModule(channel)
        self.veh_module = ...
        self.prediction_head = ...
    
    def forward(self, inf_frame, veh_frame, delta_t, filt, *args):
        h = self.veh_module(veh_frame)
        # Calling self.inf_module(inf_frame) is invalid!
        self.inf_module.trans_feats(inf_frame)
        feat1 = self.pipe.receive("feat1")
        feat2 = self.pipe.receive("feat2")
        h = torch.cat((h, feat1, feat2), 0)
        return self.prediction_head(h)
        
dataset = VICSyncDataset(split="val")
channel = Channel()
model = FusionModel(channel)
for inf_frame, veh_frame, label, delta_t, filt in dataset:
    model(inf_frame, veh_frame, delta_t, filt)
    channel.flush()
print(channel.average_bits())
```
### Matcher
We provide matching algorithms for late fusion. Currently we only provide matchers based on the distance between the center of two boxes, which is as follows:
```
class Boxes(object):
    def __init__(self, boxes, dir, label, score, class_score=None):
        ...

class EuclidianMatcher(Matcher):
    def __init__(self, filter_func=None, delta_x=0.0, delta_y=0.0, delta_z=0.0):
        ...
    
    def match(self, frame1, frame2):
        ...
```
- **Boxes** is a data structure containing a list of boxes. 
- **filter_func** is a function that decides if the two boxes are identical or not. For example, the function returns True when two boxes are from the same class and the distance bewteen their center is not larger than its width and length.
- **delta_x, delta_y, delta_z** is offset parameters. Positions in `frame1`  will automatically add [delta_x, delta_y, delta_z] before linear assignment.
- **match(frame1, frame2)** takes two frames (`Boxes` object) as input, and returns two arrays, representing matched boxes which are considered identical.

You may also implement your own matcher (such as the matcher in DeepSORT using Mahalanobis Distance and cosine similarity of features).

### Fuser

Currently we only implement a basic fuser for late fusion.

```
class BasicFuser(object):
    def __init__(self, perspective, trust_type, retain_type):
        # perspective:
        # infrastructure / vehicle
        # trust type: 
        # lc (Linear Combination) / max
        # retain type:
        # all / main / none
        
    def fuse(self, frame_i, frame_v, ind_i, ind_v):
        ...
```

The fuser takes two frames (`Boxes` object) as well as matched indexes (often calculated by `Matcher`), and returns a dictionary in the same format as ground truth labels. 

- If trust_type is lc, the final positions and confidence of the boxes are computed by linear combination. If trust_type is max, the box with higher confidence will be considered as fusion result.
- if retain_type is all, both unmatched vehicle and infrastructure boxes will be accounted into fusion results. If retain_type is main, only unmatched boxes from major perspective (defined in perspective) will be added. If retain_type is none, no unmatched box will be retained.

We plan to implement EarlyFuser, which concatenates raw information from infrastructure and vehicle, to facilitate early fusion.

### Compensator

We introduce two compensators, defined as below:

```
class SpaceCompensator(Compensator):
    def __init__(self, minx=-1.0, maxx=1.0, miny=-1.0, maxy=1.0, iters=2, steps=5):
        ...
        
    def coordinate(self, frame1, frame2):
        ...

class TimeCompensator(Compensator):
    def __init__(self, matcher):
        ...
       
    def coordinate(self, frame1, frame2, delta1, delta2):
        # frame1 is the previous frame, frame2 is the current frame
        # delta1 is time difference between frame1 and frame2
        # delta2 is time difference between frame2 and the frame we hope to predict
        ...
```

#### Space Compensator

This compensator aims to compensate for systematic error caused by physical sensors and coordinate transformation. Specifically, it evenly samples step * step points within [minx, miny, maxx, maxy], and conduct linear sum assignment. Similarly, the cost is the Eucilidian distance of box centers. The best offset value is selected based on the total cost. Then, the sample range is shrinked by a certain number, and the same process is conducted several iterations to approximate the ideal offset value.

#### Time Compensator

This compensator conducts motion compensation between temporal asynchronous frames. It leverages the previous frame to compute the speed of matched vehicles. For unmatched ones, linear regression is applied to estimate their speed. Then, it uses linear interpolation to approximate the position of vehicles delta2 milliseconds later. 

### Transformation
We provide tools to faciliate coordinate transformations (mainly rotation and translation). Here are two examples.
```
def box_translation(boxes, translation, rotation, format="mat"):
    ...
    
def points_translation(points, translation, rotation, format="mat"):
    ....
```

There are two supported formats for translation and rotation:

- mat: translation is a $3\times 1$ numpy array, and rotation is a $3\times 3$ numpy array.
- arr: translation is a array [tx, ty, tz], and rotation is a array [rw, rx, ry, rz], which is the parameters of the rotation axis.


