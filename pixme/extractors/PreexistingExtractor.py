from pydantic import FilePath

import os

from .ExtractorBase import ExtractorBase
from ..utils.path import validate_folder

class PreexistingExtractor(ExtractorBase):
    def __init__(self, folder_id: str = None, outdir: FilePath = "data"):
        super().__init__(folder_id, outdir)

        self._image_dir = os.path.join(self._image_dir, folder_id)
        self._json_dir = os.path.join(self._json_dir, folder_id)
        self._extract_dir = os.path.join(self._extract_dir, folder_id)

        validate_folder(self._image_dir)
        # validate_folder(self._json_dir)

    def _run_extraction_cycle(self):
        pass  # Because PreexistingExtractor relies on folders that already exist, no extraction cycle is needed.

    def _extract_images(self) -> None:
        raise TypeError("`PreexistingExtractor._extract_images` was somehow called when it should not have been! The files have already been extracted by definition.")

    def _extract_json(self) -> None:
        raise TypeError("`PreexistingExtractor._extract_images` was somehow called when it should not have been! The files have already been extracted by definition.")

    def _extract_files(self) -> None:
        raise TypeError("`PreexistingExtractor._extract_images` was somehow called when it should not have been! The files have already been extracted by definition.")