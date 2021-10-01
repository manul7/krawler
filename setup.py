from setuptools import setup
from app import __author__, __version__

setup(
    name='HttpCrawler',
    version=__version__,
    # license="Proprietary License",
    description="Test app",
    # platforms='any',
    keywords="http crawler test".split(), # noqa
    author=__author__,
    author_email='konstantin.belov@gmail.com',
    # url='http://TBD',
    classifiers=[
        'Development Status :: 4 - Alpha',
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
    packages=['app'],
    include_package_data=True,
    install_requires=[
        'pytz',
        'six',
        'requests',
        'beautifulsoup4',
        'click'
    ],
    entry_points={
        'console_scripts': [
            'krawl = app.crawler:cli'
        ]
    },
)
