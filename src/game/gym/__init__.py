from gymnasium.envs.registration import register

register(
    id="Taiko-v0",
    entry_point="src.game.gym.envs:TaikoEnv",
    max_episode_steps=100000
)