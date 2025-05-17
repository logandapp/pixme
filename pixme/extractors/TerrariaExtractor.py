import os
import shutil
from typing import Dict, Literal
from pydantic import FilePath

from ..utils.path import generate_temporary_folder_name, get_file_from_extension, copy_entity
from ..wrappers.terraria import *

from .ExtractorBase import ExtractorBase

TERRARIA_FOLDER = r'C:\Program Files (x86)\Steam\steamapps\common\Terraria'

class TerrariaExtractor(ExtractorBase):
    def __init__(self, file: FilePath = "terraria", outdir: FilePath = "data"):
        super().__init__(file, outdir)

        # Update directory layout.
        _raw_filename = os.path.splitext(os.path.split(file)[1])[0]
        self._image_dir = os.path.join(self._image_dir, _raw_filename)
        self._json_dir = os.path.join(self._json_dir, _raw_filename)
        self._extract_dir = os.path.join(self._extract_dir, _raw_filename)
        self._make_important_directories()

    def _extract_files(self):
        if self._file == "terraria":
            self.__extract_terraria()
            return
        self.__extract_tmod()

    def _extract_json(self):
        # This is not implemented yet; this is for phase II when I'm training
        # a transformer on a diffusion basis. I will have a lot of data, such as
        # description, crafting data, etc. on each item.
        pass

    def __extract_terraria(self):
        paths = self.__copy_terraria()
        decompile_dll(paths["exec"], self._extract_dir)
        decompile_xnbs(paths["content"], self._extract_dir)
        shutil.rmtree(os.path.dirname(paths["content"]))  # Remove temp folder

    @staticmethod
    def __copy_terraria() -> Dict[Literal["exec", "content"], FilePath]:
        exec_path = os.path.join(TERRARIA_FOLDER, 'Terraria.exe')
        cont_path = os.path.join(TERRARIA_FOLDER, 'Content')
        if not os.path.exists(exec_path) or not os.path.exists(cont_path):
            raise FileNotFoundError("Please change submodule value `extractors.TerrariaExtractor.TERRARIA_FOLDER` to the folder with the `Terraria.exe` file and the `Content` folder.")
        temp_folder = generate_temporary_folder_name()
        os.makedirs(temp_folder, exist_ok=True)

        copy_entity(exec_path, temp_folder)
        copy_entity(cont_path, temp_folder)

        return {
            "exec": os.path.join(temp_folder, 'Terraria.exe'),
            "content": os.path.join(temp_folder, 'Content')
        }

    def __extract_tmod(self):
        decompile_tmod(self._file, self._extract_dir)
        dll = get_file_from_extension(self._extract_dir, '.dll')
        decompile_dll(dll, self._extract_dir)

