import bisect

import gymnasium
import numpy as np
import pygame
import ray
from ray.rllib.algorithms.algorithm import Algorithm

from src.agent.Agent import TaikoBot
from src.game.render import TaikoEngine
from src.game.aux import Judgment, Action


def demo():
    """ Main function """
    agent = TaikoBot('./tests/test5.osu')

    env = gymnasium.make('Taiko-v0', path_to_osu='./tests/test5.osu', render_mode='human', window_size=(512, 256))
    state, info = env.reset()
    pretrained = Algorithm.from_checkpoint('./checkpoints/checkpoint_000015')
    n_steps = 50000
    score, accuracy, max_combo = 0, 0, 0
    for step in range(n_steps):
        action = pretrained.compute_single_action(state)
        state, reward, done, _, info = env.step(action)
        env.render()
        score, accuracy, max_combo = info['score'], info['accuracy'], max(max_combo, info['combo'])
        if done:
            env.reset()
            env.close()


if __name__ == "__main__":
    demo()