import os.path
import ray
from ray.rllib.algorithms.apex_dqn.apex_dqn import ApexDQNConfig
from ray.rllib.algorithms.a2c.a2c import A2CConfig
from ray.rllib.algorithms.a3c.a3c import A3CConfig
from ray.rllib.algorithms.ppo.ppo import PPOConfig
from ray import tune
import src.game.gym
from src.game.gym.envs import TaikoEnv


class TaikoBot:

    def __init__(self, path: str = os.path.join(os.getcwd(), 'tests', 'test1.osu'),
                        window_size: tuple[int, int] = (512, 256)):
        '''
        Agent class initialization
        :param path: path to `.osu` file
        :param window_size: tuple of integers, indicating the dimensions of the window
        '''
        self.last_checkpoint = None
        self.agent = None
        ray.init(ignore_reinit_error=True)
        print(path)
        # We need to register the environment first
        tune.registry.register_env('Taiko-v0', lambda config: TaikoEnv(**config))
        self.config = ApexDQNConfig().environment(
            env='Taiko-v0',
            env_config={
                'path_to_osu': path,
                'window_size': window_size
            }
        )
        self.config = self.config.resources(num_gpus=1) \
            .rollouts(num_rollout_workers=3)\
            .training(num_atoms=5)
        self.policy = None

    def train(self, save_checkpoints: bool = True, max_iter: int = 15):
        '''
        Training loop
        TODO: Replace with a GridSearch, goddangit
        :param save_checkpoints: bool
        :param max_iter: int
        :return: ray.rllib.policy.Policy()
        '''
        self.agent = self.config.build()
        for i in range(max_iter):
            result = self.agent.train()
            if save_checkpoints:
                self.last_checkpoint = self.agent.save(os.path.join('.', 'checkpoints'))

            print(f'Epoch #{i}: reward = {result["episode_reward_mean"]}, len = {result["episode_len_mean"]}')

        self.policy = self.agent.get_policy()
        return self.policy
