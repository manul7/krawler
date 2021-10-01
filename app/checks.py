from pathlib import Path
from urllib.parse import urlparse


def is_dir_exists(d: Path):
    return d.exists()


def is_url_visited(url: str):
    pass


def is_url_valid(url: str):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def is_dir_empty(dst: Path):
    if next(dst.iterdir(), None) is None:
        return True
    else:
        return False
