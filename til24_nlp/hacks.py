"""Special hacky workarounds, my favourite."""

import ctypes
import logging
import os
import sys

__all__ = ["preload_shared_libs"]

log = logging.getLogger(__name__)


def preload_shared_libs():
    """Preloading shared libs so other stuff can find them."""
    if sys.platform.startswith("linux"):
        import nvidia.cublas
        import nvidia.cuda_runtime

        ctypes.CDLL(
            os.path.join(nvidia.cublas.__path__[0], "lib", "libcublas.so.12"),
            mode=ctypes.RTLD_GLOBAL,
        )
        ctypes.CDLL(
            os.path.join(nvidia.cuda_runtime.__path__[0], "lib", "libcudart.so.12"),
            mode=ctypes.RTLD_GLOBAL,
        )

        log.warn("Linux hacks loaded.")

    # TODO: I don't remember how to do this.
    elif sys.platform == "win32":
        pass
