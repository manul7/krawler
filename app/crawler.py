#!/usr/bin/env python
# -*- coding: utf-8 -*-
from os import path
from typing import List
import click
import logging
import pathlib
import ssl

from urllib.request import Request, urlopen, urljoin, URLError
from urllib.parse import urlparse

from bs4 import BeautifulSoup

# from diskcache import Deque, Index

from .__init__ import __version__
from .checks import is_url_valid, is_dir_empty

logger = logging.getLogger(__name__)


class Crawler:
    def __init__(self, base_url: str, dst: pathlib.Path):

        if not is_url_valid(base_url):
            raise ValueError("Invalid URL.")
        # TODO: Check for ability to write in DST

        self.base_url = base_url
        self.base_dst = dst

        self.create_base_dir()
        self.crawledLinks = set()
        # Setup SSL context to ignore invalid certs
        self.ssl_ctx = ssl.create_default_context()
        self.ssl_ctx.check_hostname = False
        self.ssl_ctx.verify_mode = ssl.CERT_NONE
        self.tasks = []

    def create_base_dir(self):
        """Create output directory"""
        site_dir = urlparse(self.base_url).netloc
        save_path = pathlib.Path.joinpath(self.base_dst, site_dir)
        save_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory {save_path} created")

    def crawl(self, url: str):
        """Crawl provided link
        :param url: target URL
        """
        try:
            link = urljoin(self.base_url, url)
            is_crawled = link not in self.crawledLinks
            is_belong_base = urlparse(link).netloc == urlparse(self.base_url).netloc

            if is_belong_base and is_crawled:
                request = Request(link, headers={"User-Agent": "Mozilla/5.0"})
                response = urlopen(request, context=self.ssl_ctx)
                self.crawledLinks.add(link)
                page = response.read()
                self.save_content(urlparse(link).netloc, page)
                # Extract links
                links = self.extract_links(page)
                # Expand links
                links = [self.base_url + "/" + x for x in links]
                # Update task list
                self.enqLinks(links)

        except URLError as e:
            logger.error(
                f"URL {link} threw this error when trying to parse: {e.reason}"
            )
            return url, response.getcode()

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
            url = link.get('href')
            # TODO: handle relative URLs
            logger.debug(f"HREF: {url}")
            if is_url_valid(url):
                if urlparse(url).netloc == urlparse(self.base_url).netloc:
                    res.append(url)
            else:
                # TODO: handle relative URLs
                res.append(url)
        logger.debug(res)
        return res

    def enqLinks(self, links: List):
        for link in links:
            if urljoin(self.base_url, link) not in self.crawledLinks:
                if urljoin(self.base_url, link) not in self.tasks:
                    self.tasks.append(link)
        logger.debug(f"Links to crawl: {self.tasks}")

    def save_content(self, url: str, content: str):
        """Save page content in local storage

        :param url: URL to page
        :param content: Page's content

        Determine is URL ends with file name or not. If ends with filename - use it otherwise - generate it
        File name can be generated with condition - if target directory is empty - use "index.html" otherwise - page-<index>.html
        """

        idx = 0
        logger.debug(f"File path: {url}")
        # DST_NAME / DIR_NAME / FILE_NAME
        save_path = self.base_dst.joinpath(url)
        logger.debug(f"Save path: {save_path}")

        if is_dir_empty(save_path):
            filename = "index.html"
        else:
            filename = f"file-{idx}.html"
        file_path = save_path.joinpath(filename)
        logger.debug(f"File path: {file_path}")
        # Save content
        with open(file_path, "w") as html:
            html.write(str(content))


@click.command()
@click.version_option(version=__version__)
@click.argument("URL", metavar="<URL>")
@click.argument("DST", metavar="<DST>", type=pathlib.Path)
def cli(url, dst):
    """Krawler: Yet Another Web Crawler

    It takes URL string, processes it, and stores allowed content into DST directory.
    """
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)-8s | %(name)-15s | %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )
    try:
        crwl = Crawler(url, dst)
        res = crwl.crawl(url)
    except Exception as e:
        logger.exception(e)
        exit(1)
