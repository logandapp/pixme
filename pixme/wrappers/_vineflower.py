import subprocess
import os

from pydantic import FilePath
from .libpath import get_lib_path

def decompile_jar(jar: FilePath, copy_to: FilePath = '.') -> bool:
    if not os.path.exists(copy_to) or not os.path.isdir(copy_to):
        raise NotADirectoryError(f'Directory `{copy_to}` does not exist.')
    if not os.path.exists(jar) or not os.path.isfile(jar):
        raise FileNotFoundError(f'File `{jar}` does not exist.')
    p = subprocess.run(['java', '-jar', os.path.join(get_lib_path(), 'vineflower-1.11.1.jar'), jar, copy_to])
    if os.listdir(copy_to): return True
    return False
