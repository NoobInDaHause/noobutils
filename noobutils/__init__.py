from pathlib import Path

with open(Path(__file__).parent / "version.txt", "r") as ver:
    __version__ = ver.read()

from .converters import *
from .exceptions import *
from .views import *
from .utility import *
