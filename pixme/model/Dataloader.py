from pydantic import FilePath
from typing import Literal
import numpy as np
import torch

from ..extractors import convert_preexisting, ExtractorBase
from ..image import ImageData

Sizes = Literal['16x16', '32x32', '64x64', '128x128', '256x256']

class ImageDataloader:
    N_FILES_PER_SAMPLE: int = 128
    SIZE_MAP: dict[int, Sizes] = {
        16: '16x16',
        32: '32x32',
        64: '64x64',
        128: '128x128',
        256: '256x256'
    }

    def __init__(self, path: FilePath):
        self.__extractors = convert_preexisting(path)

    def generate_sample(self) -> dict[Sizes, np.ndarray]:
        files = ExtractorBase.sample_random(self.N_FILES_PER_SAMPLE)
        dataset = {
            '16x16': [],
            '32x32': [],
            '64x64': [],
            '128x128': [],
            '256x256': []
        }
        for file in files:
            images = ImageData(file.file).create_tiles()
            dataset[self.SIZE_MAP[images.shape[1]]].append(images)
        return {k: torch.from_numpy(np.concatenate(v, axis=0)) / 255 for k, v in dataset.items()}
