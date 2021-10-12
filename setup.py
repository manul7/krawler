from setuptools import setup
from app import __author__, __version__

try:
    from pip._internal.req import parse_requirements
except ImportError:
    from pip.req import parse_requirements

setup(
    name="HttpCrawler",
    version=__version__,
    # license="Proprietary License",
    description="Test app",
    # platforms='any',
    keywords="http crawler test".split(),  # noqa
    author=__author__,
    author_email="konstantin.belov@gmail.com",
    # url='http://TBD',
    classifiers=[
        "Development Status :: 4 - Alpha",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python",
        "Topic :: Utilities",
    ],
    packages=["app"],
    include_package_data=True,
    install_reqs = parse_requirements('requirements.txt', session='hack'),
    entry_points={"console_scripts": ["krawl = app.crawler:cli"]},
)
