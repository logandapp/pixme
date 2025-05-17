import os
from pydantic import FilePath

LIB_PATH = os.path.join(os.path.abspath(os.getcwd()), 'lib')

def change_lib_path(new_path: FilePath) -> None:
    global LIB_PATH
    LIB_PATH = new_path

def get_lib_path() -> FilePath:
    global LIB_PATH
    return LIB_PATH
