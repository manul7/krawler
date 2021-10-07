#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import List
import logging
import pathlib
import ssl
import shutil
from multiprocessing import Process

from urllib.request import Request, urlopen, URLError
from urllib.parse import urlparse

import click
from bs4 import BeautifulSoup

from diskcache import Deque, Index
from .__init__ import __version__
from .checks import is_dir_exists, is_dir_empty
from .utils import (
    expand_url,
    normalize_url,
    create_output_dir,
)
from .config import TMP_DIR

logger = logging.getLogger(__name__)


class Crawler:
    # Setup SSL context to ignore invalid certs
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE

    def __init__(self, dst: pathlib.Path):
        self.base_url = None
        self.base_dst = dst
        self.tasks = []

    def fetch(self, url: str):
        """Get page contents
        :parm url: target URL
        :return page contents
        """
        logger.debug("Fetching: %s", url)
        try:
            request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
            response = urlopen(request, context=Crawler.ssl_ctx)
            return response.read()
        except URLError as e:
            logger.error("Error '%s', while parsing %s", e.reason, url)

    def crawl(self, url):
        """Main crawling function"""
        url = expand_url(None, normalize_url(url))
        self.base_url = url
        logger.debug("Base URL: %s", self.base_url)

        create_output_dir(self.base_dst, self.base_url, url)
        urls = Deque([url], pathlib.Path.joinpath(TMP_DIR, "urls"))
        results = Index(str(pathlib.Path.joinpath(TMP_DIR, "results")))

        while True:
            try:
                url = urls.popleft()
            except IndexError:
                break

            if url in results:
                logger.debug("Skipping: %s", url)
                continue

            data = self.fetch(url)
            if data is None:
                continue

            self.save_content(url, data)
            links = self.extract_links(data)
            # Expand
            links = [expand_url(self.base_url, x) for x in links]
            logger.debug("Crawl targets: %s", links)
            urls += links
            results[url] = data

    def extract_links(self, content: str) -> List:
        """Extract and filter links

        :param content: page content
        :returns list of allowed links
        """
        res = []
        soup = BeautifulSoup(content, "html.parser")
        hrefs = soup.find_all("a")

        for link in hrefs:
            url = link.get("href")

            if url is None:
                continue

            logger.debug("HREF: %s", url)
            url = expand_url(self.base_url, normalize_url(url))

            if url.startswith(self.base_url):
                res.append(url)

        logger.debug("Extracted URLs: %s", res)
        return res

    def save_content(self, url: str, content: str):
        """Save page content to local storage

        :param url: URL to page
        :param content: Page's content

        Determine is URL ends with file name or not. If ends with filename - use it otherwise - generate it
        File name can be generated with condition - if target directory is empty - use "index.html" otherwise - page-<index>.html
        """
        idx = 0
        save_path = create_output_dir(self.base_dst, self.base_url, url)

        if is_dir_empty(save_path):
            filename = "index.html"
        else:
            filename = f"file-{idx}.html"

        file_path = save_path.joinpath(filename)
        logger.debug("File path: %s", file_path)
        # Save content
        with open(file_path, "w") as html:
            html.write(str(content))


@click.command()
@click.version_option(version=__version__)
@click.argument("URL", metavar="<URL>")
@click.argument("DST", metavar="<DST>", type=pathlib.Path)
# @click.option('--ignore-previous', is_flag=True, help='Ignore previous run and remove cache')
@click.option('--workers', default=4, help='Specify number of parallel workers')

def cli(url, dst, workers):
    """Krawler: Yet Another Web Crawler

    It takes URL string, processes it, and stores allowed content into DST directory.
    """
    logging.basicConfig(
        format="%(asctime)s | %(levelname)-8s | %(name)-15s | %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
        encoding="utf-8",
        level=logging.INFO,
    )
    if is_dir_exists(TMP_DIR):
        print(
            f"\
Previous run was found in {TMP_DIR} \
Remove previous results and restart (r) or continue (c)?"
        )
        ans = str(input())
        if ans == "r":
            targets = Index(str(pathlib.Path.joinpath(TMP_DIR, "urls")))
            targets.clear()
            results = Index(str(pathlib.Path.joinpath(TMP_DIR, "results")))
            results.clear()
            logger.warn("Cache was cleared")
            try:
                shutil.rmtree(dst)
                logger.warn("Destination directory was cleared")
            except FileNotFoundError:
                # Ignore if destination dir does not exist
                pass
        elif ans == "c":
            logger.warn("Continue")
        else:
            exit("Please choose r or c")

    try:
        crwl = Crawler(dst)
        logger.debug("Number of workers: %d", workers)
        processes = [Process(target=crwl.crawl, args=(url, )) for _ in range(workers)]

        for process in processes:
            process.start()
        for process in processes:
            process.join()

    except Exception as e:
        logger.exception(e)
        exit(1)
