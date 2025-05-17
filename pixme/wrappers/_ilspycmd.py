import subprocess
import os

from pydantic import FilePath
from .libpath import get_lib_path

def decompile_dll(dll: FilePath, copy_to: FilePath = '.') -> bool:
    if not os.path.exists(copy_to) or not os.path.isdir(copy_to):
        raise NotADirectoryError(f'Directory `{copy_to}` does not exist.')
    if not os.path.exists(dll) or not os.path.isfile(dll):
        raise FileNotFoundError(f'File `{dll}` does not exist.')
    p = subprocess.run([os.path.join(get_lib_path(), 'ILSpyCMD', 'ilspycmd'), '--nested-directories', '-p', '-o', copy_to, os.path.abspath(dll)])
    if os.listdir(copy_to): return True
    return False
