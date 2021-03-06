import logging
import pathlib
from urllib.parse import urlparse, urljoin

logger = logging.getLogger(__name__)


def create_base_dir(base_url, base_dst):
    """Create output directory"""
    site_dir = urlparse(base_url).netloc
    save_path = pathlib.Path.joinpath(base_dst, site_dir)
    save_path.mkdir(parents=True, exist_ok=True)
    logger.info("Output directory created: %s", save_path)


def normalize_url(url: str) -> str:
    """Basic normalisation func
    :param url: URL string
    :returns URL string without special characters
    """
    return url.replace("\n", "").replace("\t", "")


def expand_url(base_url, url: str) -> str:
    """Expand to standard URL scheme"""

    if base_url is not None and not (
        base_url.startswith("http") or base_url.startswith("https")
    ):
        base_url = f"http://{base_url}"

    parsed = urlparse(url, "http")

    if not parsed.netloc and base_url is not None:
        url = urljoin(base_url, url)

    if not (url.startswith("http") or url.startswith("https")):
        url = f"http://{url}"

    logger.debug("Expanded URL: %s", url)
    return url


def build_save_path(dst: pathlib.Path, base_url: str, url: str) -> pathlib.Path:
    """Build path to output dir
    :param dst: base destination directory
    :param base_url: Base URL
    :param url: Current URL
    :returns path to output dir
    """
    netloc = str(urlparse(url).netloc)
    url_path = str(urlparse(url).path)
    if url_path.startswith("/"):
        url_path = url_path[1:]

    save_path = dst.joinpath(netloc, url_path)
    logger.debug("Save path: %s", save_path)
    return save_path


def create_output_dir(dst, base_url, url) -> pathlib.Path:
    """Create output dir"""
    save_path = build_save_path(dst, base_url, url)
    logger.debug("Save path: %s", save_path)
    save_path.mkdir(exist_ok=True, parents=True)
    return save_path
