import torch.nn as nn


class BaseModel(nn.Module):
    def __init__(self, *args):
        super().__init__()

    def forward(self, inf_frame, veh_frame, delta_t, filt, *args):
        raise NotImplementedError

    @staticmethod
    def add_arguments(parser):
        pass
