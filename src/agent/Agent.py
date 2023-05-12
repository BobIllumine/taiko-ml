import os.path

import ray
from ray.rllib.algorithms.apex_dqn.apex_dqn import ApexDQNConfig
import gymnasium
from ray import tune

import src.game.gym
from src.game.gym.envs import TaikoEnv


class TaikoBot:

    def __init__(self, path: str = os.path.join(os.getcwd(), 'tests', 'test.osu')):
        self.last_checkpoint = None
        self.agent = None
        self.env = gymnasium.make('Taiko-v0', path_to_osu=path)
        ray.init(ignore_reinit_error=True)
        tune.registry.register_env('Taiko-v0', lambda config: TaikoEnv(**config))
        self.config = ApexDQNConfig().environment(
            env='Taiko-v0',
            env_config={
                'path_to_osu': path
            }
        )\
            .resources(num_gpus=1)\
            .training(lr_schedule=[[1, 1e-3, [500, 5e-3]]])\
            .rollouts(num_rollout_workers=3)
        self.model = None

    def train(self, save_checkpoints: bool = True, max_iter: int = 15):
        self.agent = self.config.build()
        for i in range(max_iter):
            result = self.agent.train()
            if save_checkpoints:
                self.last_checkpoint = self.agent.save(os.path.join('.', 'checkpoints'))

            print(f'Epoch #{i}: reward = {result}')

        self.model = self.agent.get_policy().model
        return self.model

    def evaluate(self):
        self.agent.restore(self.last_checkpoint)
        state, info = self.env.reset()
        frames, score, accuracy, max_combo = 100000, 0, 0, 0
        for i in range(frames):
            action = self.agent.compute_single_action(state)
            state, reward, done, _, info = self.env.step(action)
            score, accuracy, max_combo = info['score'], info['accuracy'], max(max_combo, info['combo'])

            self.env.render()

            if done:
                self.env.reset()
                break

        return score, accuracy, max_combo
