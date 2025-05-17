from __future__ import annotations

from pydantic import FilePath

class NullExtractor:
    singleton: NullExtractor = None

    @staticmethod
    def __new__(cls, file: FilePath = None, *_, **__):
        if NullExtractor.singleton is None:
            return super().__new__(cls)
        return NullExtractor.singleton

    def __init__(self, _: FilePath = None, *__, **___):
        NullExtractor.singleton = self

    def _get_image_dataset(self):
        pass

    def __unload_dataset(self):
        pass

    def __reload_dataset(self):
        pass

    def __clean(self):
        pass

    def _extract_files(self) -> None:
        pass

    def _extract_images(self) -> None:
        pass

    def _extract_json(self) -> None:
        pass

    def _run_extraction_cycle(self, file: FilePath = None, *_, **__):
        pass
