import os
import shutil
from pydantic import FilePath

from .path import validate_folder

# ===========================================================================
#                      IMAGE FILE PATH SHENANIGANS
# ===========================================================================

def is_image_file(filename: FilePath) -> bool:
    return filename.endswith('.png')

def copy_images_recursively(top_folder: FilePath, copy_to: FilePath) -> None:
    validate_folder(top_folder)
    validate_folder(copy_to)

    for current_folder, _, files in os.walk(top_folder):
        for file in files:
            if not is_image_file(file):
                continue
            file = os.path.join(current_folder, file)
            shutil.copy(file, copy_to)
