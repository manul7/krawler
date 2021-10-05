import logging
from pathlib import Path
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def is_dir_exists(d: Path):
    return d.exists()


def is_url_valid(url: str):
    if url is not None:
        try:
            result = urlparse(url)
            logger.debug("Result: %s", result)
            return all([result.scheme, result.netloc])
        except:
            return False
    else:
        return False


def is_dir_empty(dst: Path):
    if next(dst.iterdir(), None) is None:
        return True
    else:
        return False
