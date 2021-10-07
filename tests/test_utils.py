from os import path
import pytest
import pathlib
from app.utils import *


@pytest.mark.parametrize(
    "base, url, exp",
    [
        (None, "http://www.cwi.nl", "http://www.cwi.nl"),
        ("NOTNONE", "http://www.cwi.nl", "http://www.cwi.nl"),
        ("Base", "/data/index.html", "http://Base/data/index.html"),
        ("BBB", "dk", "http://BBB/dk"),
        ("BBB", "/dk/", "http://BBB/dk/"),
    ],
)
def test_expand_url(base, url, exp):
    assert exp == expand_url(base, url)


@pytest.mark.parametrize(
    "dst, base_url, url, exp",
    [("out", "sample", "sample", "out/sample")],
)
def test_build_save_dir(dst, base_url, url, exp):
    dst = pathlib.Path(dst)
    assert exp == str(build_save_path(dst, base_url, url))
