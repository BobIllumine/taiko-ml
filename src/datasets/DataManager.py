import os
import random
from collections import defaultdict

from PIL.Image import Image
import numpy as np


class DataManager:
    data_paths = defaultdict(lambda: '')
    def __init__(self, dataset_name: str, classes: list[str]):
        self.name = dataset_name
        self.classes = dict(zip(classes, range(len(classes))))
        self.buffer: list[tuple[Image, dict[int, list[np.array]]]] = []

    def populate(self, images: list[Image] | Image, annotations: list[dict[str, list[np.array]]]):
        self.buffer.extend(
            zip(images, list(map(lambda x: {self.classes[key]: value for key, value in x.items()}, annotations)))
        )

    def export(self, path: str, split: tuple[float, float, float] = (0.6, 0.2, 0.2), random_seed: int = -1):
        assert sum(split) == 1
        new_path = os.path.join(path, 'datasets', self.name)
        os.makedirs(new_path, exist_ok=True)
        folders = ['train', 'val', 'test']
        for f in folders:
            os.makedirs(os.path.join(new_path, f, 'images'), exist_ok=True)
            os.makedirs(os.path.join(new_path, f, 'annotations'), exist_ok=True)

        N = len(self.buffer)
        idxs = np.arange(N)

        if random_seed != -1:
            np.random.RandomState(random_seed).shuffle(idxs)

        sets = np.split(idxs, [split[0] * N, (split[0] + split[1]) * N, N])

        for i, f in enumerate(folders):
            for idx in sets[i]:
                self.buffer[idx][0].save(os.path.join(new_path, f, f'im_{idx}.png'), 'PNG')
                with open(os.path.join(new_path, f, f'im_{idx}.txt'), 'w') as txt:
                    lines = []
                    for key, value in self.buffer[idx][1].items():
                        for coords in value:
                            lines.append(' '.join([key].extend(coords.tolist())))
                    txt.writelines(lines)

        with open(os.path.join(new_path, f'{self.name}.yaml'), 'w') as yaml:
            yaml.write(f'path: {new_path}\n')
            yaml.writelines([f'{f}: {f}/images' for f in folders])
            yaml.write('names:\n')
            yaml.writelines([f'\t{key}: {value}' for key, value in self.classes])

        DataManager.data_paths[self.name] = os.path.join(new_path, f'{self.name}.yaml')

    @staticmethod
    def get_yaml_path(dataset: str) -> str | None:
        return DataManager.data_paths.get(dataset)


