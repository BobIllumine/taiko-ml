from src.game.aux import *
from bisect import bisect_right, bisect_left


class TaikoState:
    def __init__(self, notes: list[Note], od: int):
        '''
        State tracker part of a TaikoEngine
        :param notes:
        :param od: overall difficulty. Affects hit windows
        '''
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
        # Hit window mapping
        self.hit_windows = {
            Judgment.HIT300: 35 - (35 - 50) * abs(self.od - 5) / 5 if self.od < 5 else 35 + (20 - 35) * abs(self.od - 5) / 5,
            Judgment.HIT100: 80 - (80 - 120) * abs(self.od - 5) / 5 if self.od < 5 else 80 + (50 - 80) * abs(self.od - 5) / 5,
            Judgment.MISS: 95 - (95 - 135) * abs(self.od - 5) / 5 if self.od < 5 else 95 + (70 - 95) * abs(self.od - 5) / 5
        }
        # Hit keys mapping
        self.hit_key = {
            NoteType.SMALL_RED: Action.KEY_1,
            NoteType.LARGE_RED: Action.KEY_1,
            NoteType.SMALL_BLUE: Action.KEY_2,
            NoteType.LARGE_BLUE: Action.KEY_2
        }

    def __closest(self, time: int) -> tuple[int, int]:
        '''
        Rightmost less or equal and leftmost greater or equal timestamps
        :param time: requested time
        :return `tuple[int, int]` -- indices in the note list
        '''
        left, right = bisect_right(self.notes, time, key=lambda x: x.time), bisect_left(self.notes, time, key=lambda x: x.time)
        return left - 1, right

    def action(self, time: int, action: Action) -> tuple[Judgment, int]:
        '''
        Evaluate the action. Hit window and scoring information can be found here:
        https://osu.ppy.sh/wiki/en/Beatmap/Overall_difficulty
        :param time:
        :param action:
        :return: Judgement and reward value
        '''
        to_hit, idx = self.__closest(time), 0
        # Last element
        if to_hit[1] == -1:
            return Judgment.IDLE, 0
        # First unjudged note
        for i in range(to_hit[0], to_hit[1]):
            if not self.judged[i]:
                idx = i
                break
        hit_time, note_type, result, reward = abs(self.notes[idx].time - time), self.notes[idx].type, Judgment.IDLE, 0
        if hit_time <= self.hit_windows[Judgment.HIT300]:
            result = Judgment.HIT300 if action == self.hit_key[note_type] else Judgment.MISS
        elif hit_time <= self.hit_windows[Judgment.HIT100]:
            result = Judgment.HIT100 if action == self.hit_key[note_type] else Judgment.MISS
        elif hit_time <= self.hit_windows[Judgment.MISS]:
            result = Judgment.MISS if action != Action.STILL or time > self.notes[idx].time else Judgment.IDLE
        else:
            result = Judgment.GHOST if action != Action.STILL else Judgment.IDLE

        self.judged[idx] = True

        if result == Judgment.HIT300:
            self.great += 1
            self.combo += 1
            self.score += 300 + min(self.combo // 10, 10)
            reward = 300 + min(self.combo // 10, 10)
        elif result == Judgment.HIT100:
            self.good += 1
            self.combo += 1
            self.score += 100 + min(self.combo // 10, 10)
            reward = 100 + min(self.combo // 10, 10)
        elif result == Judgment.MISS:
            self.miss += 1
            self.combo = 0
        else:
            self.judged[idx] = False

        if self.great + self.good + self.miss > 0:
            self.accuracy = (self.great + 0.5 * self.good) / (self.great + self.good + self.miss)
        else:
            self.accuracy = 0
        return result, reward
