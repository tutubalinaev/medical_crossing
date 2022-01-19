# coding: utf-8

import shutil
import sys
from pathlib import Path
from typing import Callable
from functools import wraps


def cleanup_hydra(func: Callable):

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        finally:
            # replacing *.py with *.log
            log_file = Path(Path(sys.argv[0]).stem + '.log')

            if log_file.exists():
                log_file.unlink()

            hydra_dir = Path('.hydra')
            if hydra_dir.exists():
                shutil.rmtree(hydra_dir)

    return wrapper
