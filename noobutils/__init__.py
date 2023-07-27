from pathlib import Path

with open(Path(__file__).parent / "version.txt", "r") as vf:
    __version__ = vf.read()

from .converters import *
from .views import *
from .utility import *
