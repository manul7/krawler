import pytest
import app.checks


@pytest.mark.parametrize("url, exp", [
    ("http://www.cwi.nl:80/%7Eguido/Python.html", True),
    ("/data/Python.html'", False),
    ("39", False),
    (u'assdd3', False),
    ('https://stackoverflow.com', True),
    ])
def test_is_url_valud(url, exp):
    assert app.checks.is_url_valid(url) is exp
