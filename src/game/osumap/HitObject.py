from typing import NamedTuple, Any


class HitObject:
    def __init__(self, x, y, time, type, hit_sound, obj_params, hit_sample) -> None:
        self.x = int(x)
        self.y = int(y)
        self.time = int(time)
        self.type = int(type)
        self.hit_sound = int(hit_sound)
        self.obj_params = obj_params
        self.hit_sample = hit_sample

    def __str__(self):
        return "(x: " + str(self.x) + ", y: " + str(self.y) + ", tm: " + str(self.time) + ", tp: " + str(self.type) + ", sound: " + str(
            self.hit_sound) + ", o_p: " + self.obj_params + ", samp: " + self.hit_sample + ")"

    def __repr__(self):
        return self.__str__()
