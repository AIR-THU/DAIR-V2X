import numpy as np
import sys


class Channel(object):
    def __init__(self):
        self.data = {}
        self.cur_bytes = 0
        self.all_bytes = 0
        self.num_frames = 0

    def send(self, key, val):
        self.data[key] = val
        if isinstance(val, np.ndarray):
            cur_bytes = val.size * 8
        elif type(val) in [int, float]:
            cur_bytes = 8
        elif isinstance(val, list):
            cur_bytes = np.array(val).size * 8
        elif type(val) is str:
            cur_bytes = len(val)
        if key.endswith("boxes"):
            cur_bytes = cur_bytes * 7 / 24
        self.cur_bytes += cur_bytes

    def flush(self):
        self.data = {}
        self.all_bytes += self.cur_bytes
        self.cur_bytes = 0
        self.num_frames += 1

    def receive(self, key):
        return self.data[key] if key in self.data else None

    def average_bytes(self):
        num_frames = self.num_frames if len(self.data) == 0 else self.num_frames + 1
        return self.all_bytes / num_frames

    def __str__(self):
        return str(
            {
                "data": self.data,
                "cur_bytes": self.cur_bytes,
                "all_bytes": self.all_bytes,
                "num_frames": self.num_frames if len(self.data) == 0 else self.num_frames + 1,
            }
        )
