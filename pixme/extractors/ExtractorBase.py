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

from .NullExtractor import NullExtractor
from ..utils.image import copy_images_recursively
from ..utils.misc import find_partition

MIN_DATASET_SIZE = 16

class ExtractorBase(ABC):

    @dataclass
    class LabeledDataEntry:
        file: FilePath
        json: dict[str, str]

    @dataclass
    class ImplicitDataset:
        directory: FilePath
        size: int

        def __len__(self) -> int:
            return self.size

        def get(self) -> List[FilePath]:
            return os.listdir(self.directory)

        def sample(self, n: int) -> List[FilePath]:
            return random.sample(os.listdir(self.directory), n)

    SAVE_EXTRACTION: bool = False
    JSON_WARNED: bool = False  # I haven't implemented the json logic yet, so this exists to do such a thing.

    registered_extractors: dict[str, ExtractorBase] = {}
    banned_extractors: set[str] = set()
    total_size: int = 0
    partitions: list[int] = [0]

    @staticmethod
    def __new__(cls, file: FilePath = None, *_, **__):
        # Don't let duplicated extractors exist.
        id_ = os.path.split(os.path.splitext(file)[0])[1]
        if id_ in ExtractorBase.banned_extractors:
            return NullExtractor(file)
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
        self._dataset_explicit: bool = True
        self.__image_dataset_impl: ExtractorBase.ImplicitDataset | None = None
        self._dataset: List[ExtractorBase.LabeledDataEntry] = []

        # Should change the protected variables:
        #   * _dataset -> appends the image paths to _dataset.
        ExtractorBase.registered_extractors[self._id] = self

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
        self.__unload_dataset()

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

        if len(self) >= MIN_DATASET_SIZE:
            ExtractorBase.total_size += len(self)
            ExtractorBase.partitions.append(ExtractorBase.partitions[-1] + len(self))
            self.__image_dataset_impl = ExtractorBase.ImplicitDataset(self._image_dir, len(self))
        else:
            ExtractorBase.banned_extractors.add(self._id)
            del ExtractorBase.registered_extractors[self._id]

    def _make_important_directories(self) -> None:
        os.makedirs(self._image_dir, exist_ok=True)
        os.makedirs(self._json_dir, exist_ok=True)
        os.makedirs(self._extract_dir, exist_ok=True)

    @property
    def dataset(self):
        if self._dataset_explicit:
            return self._dataset
        return self.__image_dataset_impl.get()

    @property
    def size(self): return self.__len__()

    def __len__(self):
        if self._dataset_explicit:
            return len(self._dataset)
        return len(self.__image_dataset_impl)

    @abstractmethod
    def _extract_files(self) -> None: pass

    def _extract_images(self) -> None:
        copy_images_recursively(self._extract_dir, self._image_dir)

    @abstractmethod
    def _extract_json(self) -> None: pass

    def __clean(self):
        if not self.SAVE_EXTRACTION:
            shutil.rmtree(self._extract_dir, ignore_errors=True)

    def __unload_dataset(self):
        self._dataset.clear()
        self._dataset_explicit = False

    def __reload_dataset(self):
        self._dataset = self.__image_dataset_impl.get()
        self._dataset_explicit = True

    @classmethod
    def sample_random(cls, n: int = 1) -> List[ExtractorBase.LabeledDataEntry]:
        extractor_index = [find_partition(ExtractorBase.partitions, x)-1 for x in random.sample(range(ExtractorBase.total_size), n)]
        return [list(ExtractorBase.registered_extractors.values())[i_].__sample_internal() for i_ in extractor_index]

    def __sample_internal(self) -> ExtractorBase.LabeledDataEntry:
        return random.choice(self.dataset)

    def __repr__(self):
        return self._file

    @classmethod
    def __warn_json(cls):
        if cls.JSON_WARNED: return
        warnings.warn(f"Could not find corresponding .json file for image file. This warning will only play once to not spam, but be wary. Either the .json isn't implemented or something went wrong!")
