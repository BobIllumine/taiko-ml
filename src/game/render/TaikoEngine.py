import os.path

import pygame

from src.game.aux import Action, Note
from src.game.render.TaikoDisplay import TaikoDisplay
from src.game.osumap import OsuMap
from src.game.render.TaikoState import TaikoState


class TaikoEngine:

    def __init__(self, path_to_beatmap: str, width: int = 512, height: int = 256):
        assert os.path.exists(path_to_beatmap)
        with open(path_to_beatmap) as f:
            self.beatmap = OsuMap(f.read())

        self.display = TaikoDisplay(width, height, self.beatmap.notes, self.beatmap.timing_points)
        self.taiko_state = TaikoState(self.beatmap.notes, self.beatmap.od)
        self.time = 0

    def next(self, time: int, action: Action) -> tuple[pygame.surface.Surface, int]:
        assert time >= self.time
        result, reward = self.taiko_state.action(time, action)
        self.time = time
        return self.display.render_frame(time, result), reward

    def reset(self) -> None:
        self.taiko_state = TaikoState(self.beatmap.notes, self.beatmap.od)
        self.time = 0

    @property
    def judgment_line(self) -> tuple[float, float]:
        return self.display.default_offset, self.display.height / 2

    def coords(self, time: int, note: Note) -> tuple[float, float]:
        return self.display.width - ((time - note.time) * note.speed) \
               + self.display.default_offset, \
               self.display.height / 2

    def visible_notes(self, time: int) -> list[list[float]]:
        return [[*self.coords(time, note), float(note.type.value)]
                for note in sorted(self.beatmap.notes, key=lambda x: abs(time - x.time))]
                # if self.coords(time, note)[0] <= self.display.width]

    def score(self) -> tuple[int, int, float]:
        return self.taiko_state.score, self.taiko_state.combo, self.taiko_state.accuracy
