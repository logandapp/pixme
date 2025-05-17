import random
import os
import shutil

from pydantic import FilePath


def generate_random_string(length: int = 50) -> str:
    return ''.join(random.choice('abcdefghijklmnopqrstuvwxyz0123456789_') for _ in range(length))

def generate_temporary_folder_name():
    return '__temp_' + generate_random_string()

def get_file_from_extension(folder: str, extension: str) -> FilePath:
    paths = [os.path.join(folder, file) for file in os.listdir(folder) if os.path.splitext(file)[1] == extension]
    if len(paths) == 0:
        raise FileNotFoundError(f"Could not find a file with extension `{extension}` in folder `{folder}`.")
    elif len(paths) > 1:
        raise FileNotFoundError(f"Found multiple ({len(paths)}) files with extension `{extension}` in folder `{folder}`; which file to return would be ambiguous.")
    return paths[0]

def get_singleton_subfolder(folder: str) -> FilePath:
    paths = [os.path.join(folder, file) for file in os.listdir(folder) if os.path.isdir(os.path.join(folder, file))]
    if len(paths) == 0:
        raise FileNotFoundError(f"Could not find a subfolder in folder `{folder}`.")
    elif len(paths) > 1:
        raise FileNotFoundError(f"Found multiple subfolders in folder `{folder}`; which subfolder to return would be ambiguous.")
    return paths[0]

def validate_folder(folder: FilePath) -> None:
    if not os.path.exists(folder) or not os.path.isdir(folder):
        raise FileNotFoundError(f"Could not find folder `{folder}`.")

def copy_entity(to_copy: FilePath, dest: FilePath) -> None:
    if not os.path.exists(to_copy):
        raise FileNotFoundError(f"Could not find file or directory `{to_copy}`.")
    if os.path.isdir(to_copy):
        tp_lvl = os.path.join(dest, os.path.split(to_copy)[1])
        os.makedirs(tp_lvl, exist_ok=True)
        shutil.copytree(to_copy, tp_lvl, dirs_exist_ok=True)
    elif os.path.isfile(to_copy):
        shutil.copy(to_copy, dest)
