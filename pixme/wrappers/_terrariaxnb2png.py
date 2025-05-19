import subprocess
import os
import shutil
import warnings

from pydantic import FilePath

from .libpath import get_lib_path
from ..utils.path import generate_random_string

def decompile_xnbs(top: FilePath, copy_to: FilePath = '.', verbose: bool = True) -> bool:
    overall_success = False
    display_top = os.path.split(top)[1]
    print('Decoding Terraria assets...')
    for current_folder, _, files in os.walk(top):
        xnbs = []
        for file in files:
            if '.xnb' not in file:
                continue
            xnbs.append(os.path.join(current_folder, file))
        if xnbs:
            display_current = _prune_path(display_top, current_folder)
            os.makedirs(os.path.join(copy_to, display_current), exist_ok=True)
            if verbose: print(f'    Decoding .xnb to .png (Terraria asset) of `{current_folder}`...', end='')
            success = _decompile_xnbs(xnbs, os.path.join(copy_to, display_current))
            if verbose: print(f' [Done]')
            if not success:
                warnings.warn(f'Could not convert {current_folder} from .xnb to .png')
            else:
                overall_success = True

    temp_name = generate_random_string()
    curr_top = os.path.join(copy_to, display_top)
    temp_top = os.path.join(copy_to, temp_name)
    os.rename(curr_top, temp_top)
    for file in os.listdir(temp_top):
        shutil.move(os.path.join(temp_top, file), copy_to)
    os.rmdir(temp_top)

    return overall_success

def _prune_path(start: str, current: str) -> str:
    current = _splitall(current)
    current = current[current.index(start):]
    return os.path.join(*current)

def _splitall(path):
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path: # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts

def _split_files(paths: list[str], max_size: int = 28000) -> list[list[str]]:
    out = []
    bus = []
    current_length = 0
    for path in paths:
        if len(path) + current_length > max_size:
            out.append(bus)
            bus = []
            current_length = 0
        bus.append(path)
        current_length += len(path)
    if len(bus):
        out.append(bus)
    return out

def _decompile_xnbs(xnbs: list[str], copy_to: FilePath = '.') -> bool:
    if not os.path.exists(copy_to) or not os.path.isdir(copy_to):
        raise NotADirectoryError(f'Directory `{copy_to}` does not exist.')
    for xnb in xnbs:
        if not os.path.exists(xnb) or not os.path.isfile(xnb):
            raise FileNotFoundError(f'File `{xnb}` does not exist.')

    split_xnbs = _split_files(xnbs)
    for sxnbs in split_xnbs:
        p = subprocess.run([os.path.join(get_lib_path(), 'TerrariaXNB2PNG'), *sxnbs], stdout=subprocess.DEVNULL)
    for file in os.listdir(get_lib_path()):
        if os.path.splitext(file)[1] == '.xnb': os.remove(os.path.join(get_lib_path(), file))
    names = [os.path.split(os.path.splitext(xnb)[0])[1] for xnb in xnbs]
    parent_dirs = list(set(os.path.dirname(xnb) for xnb in xnbs))
    files = [os.path.join(pdir, file) for pdir in parent_dirs for file in os.listdir(pdir) if any([name in file and '.xnb' not in file and os.path.splitext(file)[1] for name in names])]
    if not files: return False

    for file in files:
        try:
            shutil.copy(file, copy_to)
            os.remove(file)
        except PermissionError:
            warnings.warn(f'Could not copy {file} to {copy_to}.')
            continue
    return True
