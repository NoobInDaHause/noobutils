with open("noobutils/version.txt", "r") as vf:
    __version__ = vf.read()

from .converters import *
from .views import *
from .utility import *
