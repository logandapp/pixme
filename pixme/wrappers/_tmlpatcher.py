import subprocess
import os

from pydantic import FilePath
from .libpath import get_lib_path

def decompile_tmod(tmod: FilePath, copy_to: FilePath = '.') -> bool:
    if not os.path.exists(copy_to) or not os.path.isdir(copy_to):
        raise NotADirectoryError(f'Directory `{copy_to}` does not exist.')
    if not os.path.exists(tmod) or not os.path.isfile(tmod):
        raise FileNotFoundError(f'File `{tmod}` does not exist.')
    p = subprocess.run([os.path.join(get_lib_path(), 'TML.Patcher', 'TML.Patcher.exe'), 'extract', tmod, '-o', copy_to])
    if os.listdir(copy_to): return True
    return False
