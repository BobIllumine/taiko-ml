class TimingPoint:
    def __init__(self, time, beat_duration, meter, sample_set, sample_idx, uninherited, effect) -> None:
        self.time = int(time)
        self.uninherited = bool(uninherited)
        self.beat_duration = None
        self.sv = None
        if uninherited:
            self.beat_duration = float(beat_duration)
        else:
            self.sv = float(beat_duration) * 100

    def __str__(self):
        return f'time: {self.time}, uninherited: {self.uninherited}, beat duration: {self.beat_duration}, sv: {self.sv}'

    def __repr__(self):
        return self.__str__()