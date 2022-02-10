import gzip
import os


def is_gzip(filename: str, ext_gzip: str = '.gz') -> bool:
    """Return whether to assume that a `filename` is Gzipped."""

    _, ext = os.path.splitext(filename)
    return ext == ext_gzip


def open_file_maybe_gzip(filename, mode):
    """Open a file an return its pointer, checking for Gzip."""

    if is_gzip(filename):
        return gzip.open(filename, mode)
    else:
        return open(filename, mode)
