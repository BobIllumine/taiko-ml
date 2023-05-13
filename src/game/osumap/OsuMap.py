import re
from bisect import bisect_left
from collections import defaultdict

from src.game.aux import *
from src.game.osumap.HitObject import HitObject
from src.game.osumap.TimingPoint import TimingPoint


class OsuMap:
    INTEGER = r"\d+"
    FLOAT = r"\d+(?:[.,]\d+)*"
    COMMA_SEPARATED_LIST = r"\w+(?:,\w+)*"
    COLON_SEPERATED_LIST = r"\w+(?:\:\w+)*"

    SECTIONS = re.compile(r"\[(?P<SECTION_NAME>\w+)\]\s(?P<SECTION_CONTENT>[^\[]+)")
    TIMING_POINT = re.compile(f"(?P<time>{INTEGER}),"
                                f"(?P<beat_duration>{FLOAT}),"
                                f"(?P<meter>{INTEGER}),"
                                f"(?P<sample_set>{INTEGER}),"
                                f"(?P<sample_idx>{INTEGER}),"
                                f"(?P<uninherited>{INTEGER}),"
                                f"(?P<effects>{INTEGER}),")
    HIT_OBJECT = re.compile(f"(?P<x>{INTEGER}),"
                            f"(?P<y>{INTEGER}),"
                            f"(?P<time>{INTEGER}),"
                            f"(?P<type>{INTEGER}),"
                            f"(?P<hit_sound>{INTEGER}),"
                            f"(?:(?P<obj_params>{COMMA_SEPARATED_LIST}),)?"
                            f"(?P<hit_sample>{COLON_SEPERATED_LIST})\:")
    DIFFICULTY = re.compile(f"HPDrainRate:(?P<hp>{FLOAT})\s"
                            f"CircleSize:(?P<cs>{FLOAT})\s"
                            f"OverallDifficulty:(?P<od>{FLOAT})\s"
                            f"ApproachRate:(?P<ar>{FLOAT})\s"
                            f"SliderMultiplier:(?P<base_sv>{FLOAT})\s"
                            f"SliderTickRate:(?P<tick_rate>{FLOAT})\s")

    def __init__(self, inputs) -> None:
        '''
        Parser for `.osu` files
        :param inputs: text
        '''
        assert isinstance(inputs, str)
        self.data = self._parse(inputs)
        self.timing_points = self.data['timing_pts']
        self.hit_objects = self.data['hit_objs']
        self.base_sv = self.data['difficulty'][4]
        self.od = self.data['difficulty'][2]
        self.notes = self._get_notes()

    def _parse(self, text):
        '''
        More details on the data format can be found at:
        https://osu.ppy.sh/wiki/en/Client/File_formats/Osu_%28file_format%29

        :param text:
        :return:
        '''
        hit_objects = []
        timing_points = []
        difficulty = []
        combined = defaultdict(lambda: [])
        # Match the regexes
        for section_name, section_content in re.findall(OsuMap.SECTIONS, text):
            if section_name == "HitObjects":
                hit_objects.extend(re.findall(OsuMap.HIT_OBJECT, section_content))
            if section_name == "TimingPoints":
                timing_points.extend(re.findall(OsuMap.TIMING_POINT, section_content))
            if section_name == "Difficulty":
                difficulty.extend(*re.findall(OsuMap.DIFFICULTY, section_content))
        combined['hit_objs'] = list(map(lambda args: HitObject(*args), hit_objects))
        combined['timing_pts'] = list(map(lambda args: TimingPoint(*args), timing_points))
        combined['difficulty'] = list(map(float, difficulty))
        return combined

    def _get_notes(self) -> list[Note]:
        '''
        Convert parsed hit objects into notes with universal speed
        :return:
        '''
        notes = []

        self.timing_points[0].sv = self.base_sv
        prev_timing = self.timing_points[0]

        # Setting the speed for each timing point
        for timing in self.timing_points[1:]:
            if not timing.uninherited:
                timing.beat_duration = prev_timing.beat_duration
                timing.sv = timing.sv * self.base_sv
            else:
                timing.sv = self.base_sv

        # Creating notes for timing points [0 : last - 1]
        for i in range(len(self.timing_points) - 1):
            prev, next = self.timing_points[i], self.timing_points[i + 1]
            for hit_obj in self._time_slice(prev.time, next.time):
                if hit_obj.hit_sound & 2 or hit_obj.hit_sound & 8:
                    n_type = NoteType.LARGE_BLUE if hit_obj.hit_sound & 4 else NoteType.SMALL_BLUE
                else:
                    n_type = NoteType.LARGE_RED if hit_obj.hit_sound & 4 else NoteType.SMALL_RED
                notes.append(Note(hit_obj.time, (prev.sv * 100) / prev.beat_duration, n_type))

        # Notes for [last : ]
        last = self.timing_points[-1]
        for hit_obj in self._time_slice(last.time):
            # 1st or 3rd bit is on -- color is blue, 2nd bit is on -- circle is large
            if hit_obj.hit_sound & 2 or hit_obj.hit_sound & 8:
                n_type = NoteType.LARGE_BLUE if hit_obj.hit_sound & 4 else NoteType.SMALL_BLUE
            else:
                n_type = NoteType.LARGE_RED if hit_obj.hit_sound & 4 else NoteType.SMALL_RED
            notes.append(Note(hit_obj.time, (last.sv * 100) / last.beat_duration, n_type))

        return notes

    def _time_slice(self, start: int, end: int = -1) -> list[Note]:
        '''
        Get the time slice
        :param start:
        :param end:
        :return:
        '''
        left = bisect_left(self.hit_objects, start, key=lambda x: x.time)
        if end == -1:
            return self.hit_objects[left:]
        right = bisect_left(self.hit_objects, end, key=lambda x: x.time)
        # print(start, end, left, right, self.beatmap.hit_objects[left], self.beatmap.hit_objects[right - 1])
        return self.hit_objects[left:right]