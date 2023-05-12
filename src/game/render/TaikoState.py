from operator import attrgetter

from src.game.aux import *
from bisect import bisect_right, bisect_left


class TaikoState:
    def __init__(self, notes: list[Note], od: int):
        self.combo = 0
        self.accuracy = 0
        self.score = 0
        self.great = 0
        self.good = 0
        self.miss = 0
        self.od = od
        self.notes = notes
        self.notes.sort(key=lambda x: x.time)
        self.judged = [False for i in range(len(self.notes))]
        self.hit_windows = {
            Judgement.HIT300: 35 - (35 - 50) * abs(self.od - 5) / 5 if self.od < 5 else 35 + (20 - 35) * abs(self.od - 5) / 5,
            Judgement.HIT100: 80 - (80 - 120) * abs(self.od - 5) / 5 if self.od < 5 else 80 + (50 - 80) * abs(self.od - 5) / 5,
            Judgement.MISS: 95 - (95 - 135) * abs(self.od - 5) / 5 if self.od < 5 else 95 + (70 - 95) * abs(self.od - 5) / 5
        }
        self.hit_key = {
            NoteType.SMALL_RED: Action.KEY_1,
            NoteType.LARGE_RED: Action.KEY_1,
            NoteType.SMALL_BLUE: Action.KEY_2,
            NoteType.LARGE_BLUE: Action.KEY_2
        }

    def __closest(self, time: int) -> tuple[int, int]:
        left, right = bisect_right(self.notes, time, key=lambda x: x.time), bisect_left(self.notes, time, key=lambda x: x.time)
        return left - 1, right

    def action(self, time: int, action: Action) -> tuple[Judgement, int]:
        # https://osu.ppy.sh/wiki/en/Beatmap/Overall_difficulty
        to_hit, idx = self.__closest(time), 0
        if to_hit[1] == -1:
            return Judgement.IDLE, 0

        for i in range(to_hit[0], to_hit[1]):
            if not self.judged[i]:
                idx = i
                break
        hit_time, note_type, result, reward = abs(self.notes[idx].time - time), self.notes[idx].type, Judgement.IDLE, 0
        if hit_time <= self.hit_windows[Judgement.HIT300]:
            result = Judgement.HIT300 if action == self.hit_key[note_type] else Judgement.MISS
        elif hit_time <= self.hit_windows[Judgement.HIT100]:
            result = Judgement.HIT100 if action == self.hit_key[note_type] else Judgement.MISS
        elif hit_time <= self.hit_windows[Judgement.MISS]:
            result = Judgement.MISS if action != Action.STILL or time > self.notes[idx].time else Judgement.IDLE
        else:
            result = Judgement.GHOST if action != Action.STILL else Judgement.IDLE

        self.judged[idx] = True

        if result == Judgement.HIT300:
            self.great += 1
            self.combo += 1
            self.score += 300 + min(self.combo // 10, 10)
            reward = 300 + min(self.combo // 10, 10)
        elif result == Judgement.HIT100:
            self.good += 1
            self.combo += 1
            self.score += 100 + min(self.combo // 10, 10)
            reward = 100 + min(self.combo // 10, 10)
        elif result == Judgement.MISS:
            self.miss += 1
            self.combo = 0
        else:
            self.judged[idx] = False

        if self.great + self.good + self.miss > 0:
            self.accuracy = (self.great + 0.5 * self.good) / (self.great + self.good + self.miss)
        else:
            self.accuracy = 0
        return result, reward
