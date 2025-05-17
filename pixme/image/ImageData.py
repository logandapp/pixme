from PIL import Image
import numpy as np
import random

from pydantic import FilePath

MIN_TILE_SIZE = 16
MAX_TILE_SIZE = 256

def pad_to_power_of_two_square(arr: np.ndarray, random_pad: bool = True) -> np.ndarray:
    _, h, w = arr.shape[:3]

    # Step 1: Crop if too big
    off_x, off_y = 0, 0
    if random_pad and h > MAX_TILE_SIZE:
        off_y = random.randint(0, h - MAX_TILE_SIZE - 1)
    if random_pad and w > MAX_TILE_SIZE:
        off_x = random.randint(0, w - MAX_TILE_SIZE - 1)

    cropped = arr[off_y:min(h, MAX_TILE_SIZE)+off_y, off_x:min(w, MAX_TILE_SIZE)+off_x]
    _, h, w = cropped.shape[:3]

    # Step 2: Find next power of two for both dimensions (not exceeding max_size)
    target_size = 2 ** int(np.ceil(np.log2(max(h, w))))
    target_size = min(target_size, MAX_TILE_SIZE)

    # Step 3: Pad to square power of two
    pad_height = target_size - h
    pad_width = target_size - w

    pad_x, pad_y = 0, 0
    if random_pad and pad_width:
        pad_x = random.randint(0, pad_width-1)
    if random_pad and pad_height:
        pad_y = random.randint(0, pad_height - 1)

    if arr.ndim == 2:
        padded = np.pad(cropped, ((pad_y, pad_height-pad_y), (pad_x, pad_width-pad_x)), mode='constant')
    elif arr.ndim == 3:
        # 1 image
        padded = np.pad(cropped, ((pad_y, pad_height-pad_y), (pad_x, pad_width-pad_x), (0, 0)), mode='constant')
    else:
        # array of images
        padded = np.pad(cropped, ((0, 0), (pad_y, pad_height-pad_y), (pad_x, pad_width-pad_x), (0, 0)), mode='constant')

    return padded

class ImageData:
    def __init__(self, file: FilePath, data: dict = None):
        self.image_file = Image.open(file).convert('RGBA')
        self._image = None
        self._grayscale = None
        self.data = data
        if data is None:
            self.data = {}

    @property
    def image(self):
        if self._image is None:
            self._image = np.array(self.image_file)
        return self._image

    @property
    def grayscale(self):
        if self._grayscale is None:
            self._grayscale = np.array(self.image_file.convert("L"))
        return self._grayscale

    def create_tiles(self):
        h, w, _ = self.image.shape
        t_x, t_y = self._detect_periodic()

        n_h = h // t_y
        n_w = w // t_x

        if h % t_y != 0 or n_h < MIN_TILE_SIZE: t_y, n_h = 1, h
        if w % t_x != 0 or n_w < MIN_TILE_SIZE: t_x, n_w = 1, w

        return pad_to_power_of_two_square(self.image.reshape(t_y, n_h, t_x, n_w, 4).transpose(0, 2, 1, 3, 4).reshape(t_y*t_x, n_h, n_w, 4))

    @staticmethod
    def __vertical_channel_fft(c_data: np.ndarray) -> np.ndarray:
        return np.sum(np.abs(np.fft.fft(c_data - np.mean(c_data, axis=0, keepdims=True), axis=0)), axis=1)

    @staticmethod
    def __horizontal_channel_fft(c_data: np.ndarray) -> np.ndarray:
        return np.sum(np.abs(np.fft.fft(c_data - np.mean(c_data, axis=1, keepdims=True), axis=1)), axis=0)

    def _detect_periodic(self):
        v_fft = self.__vertical_channel_fft(self.grayscale)
        v_freqs = np.fft.fftfreq(v_fft.shape[0], 1.0 / v_fft.shape[0])

        h_fft = self.__horizontal_channel_fft(self.grayscale)
        h_freqs = np.fft.fftfreq(h_fft.shape[0], 1.0 / h_fft.shape[0])

        return round(abs(h_freqs[np.argmax(h_fft)])), round(abs(v_freqs[np.argmax(v_fft)]))
