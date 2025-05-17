import subprocess
import os
import shutil
import zipfile

from pydantic import FilePath
from .libpath import get_lib_path
from ..utils.path import get_file_from_extension, generate_temporary_folder_name, get_singleton_subfolder, copy_entity

def decompile_minecraft(version: str = 'latest', copy_to: FilePath = '.', delete_versions: bool = True) -> bool:
    if not os.path.exists(copy_to) or not os.path.isdir(copy_to):
        raise NotADirectoryError(f'Directory `{copy_to}` does not exist.')
    mc_path = os.path.join(get_lib_path(), 'DecompilerMC')
    p = subprocess.run(['python', os.path.join(mc_path, 'main.py'), '--mcversion', version, '-c', '-f'])
    src_path = os.path.join(mc_path, 'src')

    shutil.copytree(os.path.join(src_path, os.listdir(src_path)[0]), copy_to, dirs_exist_ok=True)

    # Cleanup that DecompilerMC doesn't do :/
    shutil.rmtree(src_path)
    shutil.rmtree(os.path.join(mc_path, 'mappings'))
    shutil.rmtree(os.path.join(mc_path, 'tmp'))

    nested_folder = get_singleton_subfolder(os.path.join(mc_path, 'versions'))
    jar = get_file_from_extension(nested_folder, '.jar')
    temp_folder = os.path.join(nested_folder, generate_temporary_folder_name())
    os.makedirs(temp_folder, exist_ok=True)
    with zipfile.ZipFile(jar, 'r') as jar_file:
        jar_file.extractall(temp_folder)
    copy_entity(os.path.join(temp_folder, 'assets'), copy_to)

    shutil.rmtree(os.path.join(mc_path, 'versions'))

    if os.listdir(copy_to): return True
    return False
