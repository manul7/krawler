#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import List
import logging
import pathlib
import ssl
import shutil

from urllib.request import Request, urlopen, URLError
from urllib.parse import urlparse

import click
from bs4 import BeautifulSoup

from diskcache import Deque, Index
from .__init__ import __version__
from .checks import is_dir_exists, is_url_valid, is_dir_empty
from .utils import expand_url, normalize_url, create_base_dir
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
            response = urlopen(request, context=self.ssl_ctx)
            return response.read()
        except URLError as e:
            logger.error("Error '%s', while parsing %s", e.reason, url)

    def crawl(self, url):
        """Main crawling function"""
        url = expand_url(None, normalize_url(url))
        self.base_url = url
        logger.debug("Base URL: %s", self.base_url)

        if not is_url_valid(self.base_url):
            raise ValueError("Invalid URL.")

        create_base_dir(self.base_url, self.base_dst)

        urls = Deque([url], pathlib.Path.joinpath(TMP_DIR, "urls"))
        results = Index(str(pathlib.Path.joinpath(TMP_DIR, "results")))

        while True:
            try:
                url = urls.popleft()
            except IndexError:
                break

            if url in results:
                continue

            data = self.fetch(url)
            if data is None:
                continue

            self.save_content(url, data)
            links = self.extract_links(data)
            # Expand
            links = [expand_url(self.base_url, x) for x in links]
            logger.debug("Links: %s", links)
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
        # TODO: Move to separate func, if more flexibility required
        for link in hrefs:
            url = link.get("href")

            if url is None:
                continue

            # TODO: handle relative URLs
            logger.debug("HREF: %s", url)
            url = normalize_url(url)

            if is_url_valid(url):
                if url.startswith(self.base_url):
                    res.append(url)
            else:
                # TODO: handle relative URLs
                res.append(url)
        logger.debug("Results list: %s", res)
        return res

    def save_content(self, url: str, content: str):
        """Save page content in local storage

        :param url: URL to page
        :param content: Page's content

        Determine is URL ends with file name or not. If ends with filename - use it otherwise - generate it
        File name can be generated with condition - if target directory is empty - use "index.html" otherwise - page-<index>.html
        """
        idx = 0

        # DST_NAME / DIR_NAME / FILE_NAME
        netloc = str(urlparse(url).netloc)
        url_path = str(urlparse(url).path)
        logger.debug("Base URL: %s", netloc)
        logger.debug("URL path: %s", url_path)
        # Note: Skip /
        save_path = self.base_dst.joinpath(netloc, url_path[1:])
        logger.debug("Save path: %s", save_path)

        save_path.mkdir(exist_ok=True, parents=True)
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
def cli(url, dst):
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
        crwl.crawl(url)

    except Exception as e:
        logger.exception(e)
        exit(1)
