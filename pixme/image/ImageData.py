from PIL import Image
import numpy as np
from scipy.ndimage import convolve
from scipy.signal import find_peaks
from scipy.stats import mode
import random

from pydantic import FilePath

CUTOFF_PERCENTILE = 95
TILE_CUTOFF = 0.07
MIN_TILE_SIZE = 16
MAX_TILE_SIZE = 256
KERNEL = np.ones((64, 64)) / (64*64)
EPS = 1e-8

def pad_to_power_of_two_square(arr: np.ndarray, random_pad: bool = True) -> np.ndarray | None:

    empty_images = np.sum(arr, axis=(1, 2, 3)) == 0
    arr = np.delete(arr, empty_images, axis=0)
    empty_x = np.sum(arr, axis=(0, 1, 3)) == 0
    arr = np.delete(arr, empty_x, axis=2)
    empty_y = np.sum(arr, axis=(0, 2, 3)) == 0
    arr = np.delete(arr, empty_y, axis=1)

    _, h, w = arr.shape[:3]

    # Step 1: Crop if too big
    off_x, off_y = 0, 0
    if random_pad and h > MAX_TILE_SIZE:
        off_y = random.randint(0, h - MAX_TILE_SIZE - 1)
    if random_pad and w > MAX_TILE_SIZE:
        off_x = random.randint(0, w - MAX_TILE_SIZE - 1)

    cropped = arr[:, off_y:min(h, MAX_TILE_SIZE)+off_y, off_x:min(w, MAX_TILE_SIZE)+off_x]
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
        t_y, t_x = self._detect_periodic()

        t_x = self.__round_tiling(w, t_x)
        t_y = self.__round_tiling(h, t_y)

        n_w, n_h = w // t_x, h // t_y

        return pad_to_power_of_two_square(self.image.reshape(t_y, n_h, t_x, n_w, 4).transpose(0, 2, 1, 3, 4).reshape(t_y*t_x, n_h, n_w, 4))

    @staticmethod
    def __round_tiling(s: int, t: int):
        if np.isnan(t):
            return 1

        appr = s / round(s / t)
        if appr % 1:
            return 1

        if abs(t - appr) / appr <= TILE_CUTOFF:
            if s // t >= MIN_TILE_SIZE:
                return round(appr)

            # Just in the chance that there's a vertical pattern that's throwing us off.
            elif appr % 4 == 0 and s // t >= MIN_TILE_SIZE // 4:
                return round(appr / 4)
            elif appr % 2 == 0 and s // t >= MIN_TILE_SIZE // 2:
                return round(appr / 2)

        return 1

    @staticmethod
    def __vertical_channel_fft(c_data: np.ndarray) -> np.ndarray:
        return np.fft.fft(c_data, axis=0)

    @staticmethod
    def __horizontal_channel_fft(c_data: np.ndarray) -> np.ndarray:
        return np.fft.fft(c_data, axis=1)

    @staticmethod
    def __reduce_parallel_fft(fft_data: np.ndarray, axis: int) -> np.ndarray:
        return np.sum(np.abs(fft_data), axis=axis)

    @staticmethod
    def __extract_dominant_frequency(fft_data: np.ndarray, fft_freqs: np.ndarray) -> int:
        spectra = np.abs(fft_data)
        spectra[spectra < np.percentile(spectra, CUTOFF_PERCENTILE)] = 0.0
        freqs = np.diff(np.sort(fft_freqs[find_peaks(spectra)[0]]))
        freqs = freqs[freqs >= MIN_TILE_SIZE // 4]
        if freqs.size:
            return mode(freqs).mode
        return fft_freqs[np.argmax(spectra)]

    def _detect_periodic(self):
        pixel_mask = convolve(self.image[:, :, 3], KERNEL, mode='nearest').astype(bool).astype(float)  # alpha mask

        v_freqs = np.fft.fftfreq(pixel_mask.shape[0], 1.0 / pixel_mask.shape[0])
        h_freqs = np.fft.fftfreq(pixel_mask.shape[1], 1.0 / pixel_mask.shape[1])
        v_tot = None
        h_tot = None

        for channel in [self.image[:, :, 0], self.image[:, :, 1], self.image[:, :, 2]]:
            pixel_img = channel * pixel_mask / 255

            v_fft = self.__vertical_channel_fft(pixel_img)
            v_fmask = self.__vertical_channel_fft(pixel_mask)
            v_fnorm = v_fft / (v_fmask + EPS)
            v_trans = self.__reduce_parallel_fft(v_fnorm, axis=1)
            if v_tot is None: v_tot = v_trans
            else: v_tot += v_trans

            h_fft = self.__horizontal_channel_fft(pixel_img)
            h_fmask = self.__horizontal_channel_fft(pixel_mask)
            h_fnorm = h_fft / (h_fmask + EPS)
            h_trans = self.__reduce_parallel_fft(h_fnorm, axis=0)
            if h_tot is None: h_tot = h_trans
            else: h_tot += h_trans

        return self.__extract_dominant_frequency(v_trans, v_freqs), self.__extract_dominant_frequency(h_trans, h_freqs)
