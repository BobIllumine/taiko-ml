import bisect

import numpy as np
import pygame

from src.agent.Agent import TaikoBot
from src.game.render import TaikoEngine
from src.game.aux import Judgement, Action
from pygame.locals import (
    QUIT,
    KEYDOWN,
    K_j,
    K_k,
    K_h,
    K_g,
)


def demo():
    """ Main function """
    agent = TaikoBot('./tests/test.osu')
    print(agent.train())
    print(agent.evaluate())

if __name__ == "__main__":
    demo()
    # tup = (1, 2, 3)
    # lst = [*tup, 4]
    # print(lst)