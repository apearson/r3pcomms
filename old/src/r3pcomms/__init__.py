"""
River 3 Plus comms from scratch via USB CDC (ACM)
"""

from ._r3pcomms import R3PComms
from ._version import version

__version__ = version

__all__ = [
    "R3PComms",
    "__version__",
]


def __dir__() -> list[str]:
    return __all__
