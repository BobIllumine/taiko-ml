import gymnasium as gym
import numpy as np
import pygame.time

from gymnasium import spaces

from src.game.render import TaikoEngine
from src.game.aux import *


class TaikoEnv(gym.Env):

    metadata = {'render_modes': ['human', 'rgb_array'], 'render_fps': 240}

    def __init__(self, render_mode: str = None, path_to_osu: str = './tests/test1.osu', window_size: tuple = (512, 256)):
        '''
        TODO: This whole class needs to be rewritten

        Custom Gym for training
        :param render_mode:
        :param path_to_osu:
        :param window_size:
        '''
        self.window_size = window_size
        self.path_to_osu = path_to_osu

        # Agent here - (x, y) coordinates
        # Target - 3 notes represented by (x, y, type, speed)
        self.observation_space = spaces.Dict(
            {
                'agent': spaces.Box(np.array([0, 0]), np.array([self.window_size[0], self.window_size[1]]), shape=(2,)),
                'target': spaces.Box(np.array([[-np.inf, 0, 0, 0],
                                               [-np.inf, 0, 0, 0],
                                               [-np.inf, 0, 0, 0]]),
                                     np.array([[np.inf, self.window_size[1], 3, np.inf],
                                               [np.inf, self.window_size[1], 3, np.inf],
                                               [np.inf, self.window_size[1], 3, np.inf]]),
                                     shape=(3, 4))
            }
        )
        # Press KEY_1, KEY_2 or nothing at all
        self.action_space = spaces.Discrete(3)

        self._engine = TaikoEngine(path_to_osu, self.window_size[0], self.window_size[1])

        self._action_map = {
            0: Action.STILL,
            1: Action.KEY_1,
            2: Action.KEY_2
        }
        self._time = 0
        self._last_action = Action.STILL

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self._last_scene = None
        self.clock = None
        self.render_mode = render_mode
        self.window = None

    def _get_obs(self):
        '''
        Most probably the bottleneck right there
        :return:
        '''
        return {'agent': np.array(self._engine.judgment_line, dtype=np.float32),
                'target': np.array(self._engine.visible_notes(self._time)[:3], dtype=np.float32)}

    def _get_info(self):
        '''
        Metrics as info
        :return:
        '''
        score, combo, acc = self._engine.score()
        return {'score': score, 'combo': combo, 'accuracy': acc}

    def step(self, action: int):
        '''
        Updates an in-game timer. Notice that it de-synchronizes it from pygame.Clock
        :param action:
        :return:
        '''
        assert action in self._action_map.keys()

        self._time += 1000 // self.metadata['render_fps']
        self._last_action = self._action_map[action]
        self._last_scene, reward = self._engine.next(self._time, self._last_action)

        observation, info, done = self._get_obs(), self._get_info(), self._time > self._engine.beatmap.notes[-1].time + 1000

        if self.render_mode == 'human':
            self._render_frame()

        return observation, reward, done, False, info

    def reset(self, seed=None, options=None):
        '''
        Reset function of the gym. No seed needed since there is no random
        :param seed:
        :param options:
        :return:
        '''
        super().reset(seed=seed)
        self._time = 0
        self._last_action = Action.STILL
        self._engine.reset()
        self._last_scene, _ = self._engine.next(self._time, self._last_action)

        observation = self._get_obs()
        # print(observation, observation['agent'].shape, observation['target'].shape)
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, info

    def render(self):
        if self.render_mode == 'rgb_array':
            return self._render_frame()

    def _render_frame(self):
        if self.window is None and self.render_mode == "human":
            pygame.init()
            pygame.display.init()
            self.window = pygame.display.set_mode(self.window_size)

        if self.clock is None and self.render_mode == "human":
            self.clock = pygame.time.Clock()

        if self.render_mode == "human":
            # The following line copies our drawings to the visible window
            self.window.blit(self._last_scene, self._last_scene.get_rect())
            pygame.display.set_caption(f'score: {self._engine.score()[0]}, accuracy: {self._engine.score()[2]:.2f}')
            pygame.event.pump()
            pygame.display.update()
            # We need to ensure that human-rendering occurs at the predefined framerate.
            # The following line will automatically add a delay to keep the framerate stable.
            self.clock.tick(self.metadata["render_fps"])
        else:  # rgb_array
            return np.transpose(
                np.array(pygame.surfarray.pixels3d(self._last_scene)), axes=(1, 0, 2)
            )

    def close(self):
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()
