from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass

from pydantic import FilePath
from typing import List

import os
import random
import shutil
import json
import warnings

from ..utils.image import copy_images_recursively
from ..utils.misc import find_partition

class ExtractorBase(ABC):

    @dataclass
    class LabeledDataEntry:
        file: FilePath
        json: dict[str, str]

    SAVE_EXTRACTION: bool = False
    JSON_WARNED: bool = False  # I haven't implemented the json logic yet, so this exists to do such a thing.

    registered_extractors: dict[str, ExtractorBase] = {}
    total_size: int = 0
    partitions: list[int] = [0]

    @staticmethod
    def __new__(cls, file: FilePath = None, *_, **__):
        # Don't let duplicated extractors exist.
        id_ = os.path.split(os.path.splitext(file)[0])[1]
        if id_ in ExtractorBase.registered_extractors:
            return ExtractorBase.registered_extractors[id_]
        return super().__new__(cls)

    def __init__(self, file: FilePath = None, outdir: FilePath = "data"):
        # Ensure existence of outdir
        if file is None:
            raise ValueError(f"Please specify a filename when instantiating \"{self.__class__.__name__}\"...")
        if not os.path.exists(outdir):
            raise FileNotFoundError(f"Please create the folder \"{os.path.join(os.getcwd(), 'data', 'image')}\"..")

        # Important directories
        self._image_dir = os.path.join(outdir, "image")
        self._json_dir = os.path.join(outdir, "json")
        self._extract_dir = os.path.join(outdir, "extract")

        self._make_important_directories()

        # Used later for sampling :)
        self._file = file
        self._id = os.path.split(os.path.splitext(self._file)[0])[1]
        self._dataset: List[ExtractorBase.LabeledDataEntry] = []

        # Should change the protected variables:
        #   * _dataset -> appends the image paths to _dataset.
        ExtractorBase.registered_extractors[file] = self

    def __init_subclass__(cls, *args, **kwargs):
        # All this does is add an after_init hook after the subclasses' init function :)
        super().__init_subclass__(**kwargs)
        og_init = cls.__init__

        def new_init(self, *args, **kwargs):
            og_init(self, *args, **kwargs)
            self.__after_init__()

        cls.__init__ = new_init

    def __after_init__(self):
        # This is the hook that gets inserted after the subclasses' init. Add more if needed.
        self._run_extraction_cycle()
        self._get_image_dataset()

    def _run_extraction_cycle(self):
        self._extract_files()
        self._extract_images()
        self._extract_json()
        self.__clean()

    def _get_image_dataset(self):
        for file in os.listdir(self._image_dir):
            image_file = os.path.join(self._image_dir, file)
            json_file = os.path.join(self._json_dir, os.path.splitext(file)[0] + ".json")

            if not os.path.isfile(json_file):
                image_json = {}
                self.__warn_json()
            else:
                image_json = json.load(open(json_file))

            self._dataset.append(ExtractorBase.LabeledDataEntry(image_file, image_json))

        if len(self):
            ExtractorBase.total_size += len(self)
            ExtractorBase.partitions.append(ExtractorBase.partitions[-1] + len(self))
        else:
            del ExtractorBase.registered_extractors[self._id]

    def _make_important_directories(self) -> None:
        os.makedirs(self._image_dir, exist_ok=True)
        os.makedirs(self._json_dir, exist_ok=True)
        os.makedirs(self._extract_dir, exist_ok=True)

    @property
    def size(self): return self.__len__()
    def __len__(self): return len(self._dataset)

    @abstractmethod
    def _extract_files(self) -> None: pass

    def _extract_images(self) -> None:
        copy_images_recursively(self._extract_dir, self._image_dir)

    @abstractmethod
    def _extract_json(self) -> None: pass

    def __clean(self):
        if not self.SAVE_EXTRACTION:
            shutil.rmtree(self._extract_dir, ignore_errors=True)

    @classmethod
    def sample_random(cls, n: int = 1) -> List[ExtractorBase.LabeledDataEntry]:
        extractor_index = [find_partition(ExtractorBase.partitions, x)-1 for x in random.sample(range(ExtractorBase.total_size), n)]
        return [list(ExtractorBase.registered_extractors.values())[i_].__sample_internal() for i_ in extractor_index]

    def __sample_internal(self) -> ExtractorBase.LabeledDataEntry:
        return random.choice(self._dataset)

    def __repr__(self):
        return self._file

    @classmethod
    def __warn_json(cls):
        if cls.JSON_WARNED: return
        warnings.warn(f"Could not find corresponding .json file for image file. This warning will only play once to not spam, but be wary. Either the .json isn't implemented or something went wrong!")
