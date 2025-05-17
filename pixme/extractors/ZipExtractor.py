import zipfile
import os

from pydantic import FilePath

from .ExtractorBase import ExtractorBase

class ZipExtractor(ExtractorBase):
    def __init__(self, file: FilePath = None, outdir: FilePath = "data"):
        super().__init__(file, outdir)

        # Update directory layout.
        _raw_filename = os.path.splitext(os.path.split(file)[1])[0]
        self._image_dir = os.path.join(self._image_dir, _raw_filename)
        self._json_dir = os.path.join(self._json_dir, _raw_filename)
        self._extract_dir = os.path.join(self._extract_dir, _raw_filename)
        self._make_important_directories()

    def _extract_files(self) -> None:
        with zipfile.ZipFile(self._file, 'r') as zf:
            zf.extractall(self._extract_dir)

    def _extract_json(self) -> None:
        # This is not implemented yet; this is for phase II when I'm training
        # a transformer on a diffusion basis. I will have a lot of data, such as
        # description, crafting data, etc. on each item.
        pass
