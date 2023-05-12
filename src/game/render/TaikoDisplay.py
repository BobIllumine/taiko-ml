import pygame
from src.game.aux import *
from src.game.osumap import TimingPoint

SCREEN_WIDTH = 512
SCREEN_HEIGHT = 256
SCREEN_TITLE = "osu!taiko simplistic render"


class TaikoDisplay:
    NOTE_MAP = {
        NoteType.SMALL_RED: lambda rad: (pygame.Color('orangered3'), rad),
        NoteType.LARGE_RED: lambda rad: (pygame.Color('orangered3'), rad * 1.3),
        NoteType.SMALL_BLUE: lambda rad: (pygame.Color('steelblue2'), rad),
        NoteType.LARGE_BLUE: lambda rad: (pygame.Color('steelblue2'), rad * 1.3),

    }
    JUDGEMENT_MAP = {
        Judgement.GHOST: lambda jud_rad: (pygame.Color('grey85'), jud_rad * 1.05),
        Judgement.IDLE: lambda jud_rad: (pygame.Color('grey61'), jud_rad),
        Judgement.MISS: lambda jud_rad: (pygame.Color('firebrick1'), jud_rad * 0.9),
        Judgement.HIT100: lambda jud_rad: (pygame.Color('lightgreen'), jud_rad * 1.1),
        Judgement.HIT300: lambda jud_rad: (pygame.Color('yellow1'), jud_rad * 1.2),
    }

    def __init__(self, width: int, height: int, hit_objs: list[Note], timing_pts: list):
        self.width = width
        self.height = height
        self.hit_objects = hit_objs
        self.default_rad = width * 0.05
        self.default_offset = width * 0.1
        self.timing_pts = timing_pts

    def _draw_note(self, surf: pygame.Surface, time: int, note: Note):
        color, rad = TaikoDisplay.NOTE_MAP[note.type](self.default_rad)
        pygame.draw.circle(
            surf,
            color,
            (self.width - ((time - note.time) * note.speed) + self.default_offset, self.height / 2),
            rad
        )
        pygame.draw.circle(
            surf,
            pygame.Color('snow2'),
            (self.width - ((time - note.time) * note.speed) + self.default_offset, self.height / 2),
            rad + 1,
            5
        )

    def _draw_judgement(self, surf: pygame.Surface, judgement: Judgement):
        color, rad = TaikoDisplay.JUDGEMENT_MAP[judgement](self.default_rad)
        pygame.draw.circle(
            surf,
            color,
            (self.default_offset, self.height / 2),
            rad
        )

    def _draw_timing_line(self, surf: pygame.Surface, time: int, timing_pt: TimingPoint):
        pygame.draw.line(
            surf,
            pygame.Color('snow2'),
            (self.width - ((time - timing_pt.time) * ((timing_pt.sv * 100) / timing_pt.beat_duration)) + self.default_offset, self.height / 2 - self.default_rad * 2),
            (self.width - ((time - timing_pt.time) * ((timing_pt.sv * 100) / timing_pt.beat_duration)) + self.default_offset, self.height / 2 + self.default_rad * 2),
            1
        )

    def render_frame(self, cur_time: int, judgement: Judgement):
        canvas = pygame.Surface((self.width, self.height))
        self._draw_judgement(canvas, judgement)
        for hit_obj in self.hit_objects:
            if self.width - ((cur_time - hit_obj.time) * hit_obj.speed) < 0:
                continue
            # print(f'{hit_obj.time=}, {hit_obj.speed=}, {hit_obj.type=}')
            self._draw_note(canvas, cur_time, hit_obj)
        for timing_pt in self.timing_pts:
            if self.width - ((cur_time - timing_pt.time) * ((timing_pt.sv * 100) / timing_pt.beat_duration)) < 0:
                continue
            # print(f'{timing_pt.time=}, {timing_pt.sv=}')
            self._draw_timing_line(canvas, cur_time, timing_pt)
        return canvas

