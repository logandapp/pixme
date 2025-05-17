import os

from .MinecraftExtractor import MinecraftExtractor
from .TerrariaExtractor import TerrariaExtractor
from .PreexistingExtractor import PreexistingExtractor
from .ZipExtractor import ZipExtractor

from .ExtractorBase import ExtractorBase
from pydantic import FilePath
from typing import List, Type


def convert_preexisting(folder: FilePath = "data/image", outdir: FilePath = "data") -> List[Type[ExtractorBase]]:
    extractors = []
    for path in os.listdir(folder):
        extractors.append(PreexistingExtractor(path, outdir=outdir))
    return extractors

def convert_executables(folder: FilePath, outdir: FilePath = "data") -> List[Type[ExtractorBase]]:
    extractors = []
    for file in os.listdir(folder):
        file = os.path.join(folder, file)
        if file.endswith(".jar"):
            extractors.append(MinecraftExtractor(file, outdir=outdir))
        elif file.endswith(".tmod"):
            extractors.append(TerrariaExtractor(file, outdir=outdir))
        elif file.endswith(".zip"):
            extractors.append(ZipExtractor(file, outdir=outdir))
    return extractors
