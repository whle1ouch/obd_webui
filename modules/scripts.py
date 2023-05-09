import os

from .paths import script_path
import modules.extensions


def list_files_with_name(filename):
    res = []

    dirs = [script_path] + [ext.path for ext in extensions.active()]

    for dirpath in dirs:
        if not os.path.isdir(dirpath):
            continue

        path = os.path.join(dirpath, filename)
        if os.path.isfile(path):
            res.append(path)

    return res