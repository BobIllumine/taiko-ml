from enum import Enum
from src.game.osumap import OsuMap

import numpy as np


class Action(Enum):
    KEY1 = -1,
    KEY2 = 1,
    STILL = 0


class TaikoState:
    def __init__(self) -> None:
        self.t = 0
        self.combo = 0
        self.hp = 0
        self.score = 0
        self.miss_count = 0
        self.hit_objects = []

    def slice(self, start_time, end_time=0):
        l, r = 0, len(self.hit_objects)
        while r - l > 1:
            m = (r + l) >> 1
            if self.hit_objects[m].time <= end_time:
                l = m
            else:
                r = m
        right = l
        l, r = -1, len(self.hit_objects) - 1
        while r - l > 1:
            m = (r + l) >> 1
            if self.hit_objects[m].time >= start_time:
                r = m
            else:
                l = m
        return self.hit_objects[r:(right + 1)]


    def last(self):
        return self.hit_objects[:-1]

    def update(self, action: Action, time: np.uint16):
        closest = self.slice(time)
        print(closest, action)


class Taiko:
    def __init__(self) -> None:
        self.state: TaikoState = None

    def load(self, osu: OsuMap):
        self.state = TaikoState()
        self.state.hit_objects = sorted(osu.data['hit_objs'], key=lambda x: x.time)

    def next(self, action: Action, time: np.uint16):
        self.t = time
        self.state.update(action, time)

