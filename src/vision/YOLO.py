from roboflow import Roboflow
from ultralytics import YOLO
from PIL.Image import Image
from src.datasets.DataManager import DataManager


class YOLOVision:
    def __init__(self, path: str='yolov8n.pt'):
        self.model = YOLO(path)

    def train(self, dataset: str, **kwargs):
        path = DataManager.get_yaml_path(dataset)
        if path is None:
            raise KeyError(f'Cannot find the dataset with the name `{dataset}`')
        self.model.train(data=path, **kwargs)

    def scan(self, image: Image):
        results = self.model(image)
        