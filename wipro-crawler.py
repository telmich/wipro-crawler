#!/usr/bin/env python3

import sys
import argparse
import logging
import subprocess
import os
from os.path import join
from html.parser import HTMLParser

version="0.1"
wget=['wget', '--mirror', '-A', '*.html,*.php,*.asp']

log = logging.getLogger()
logging.basicConfig(format='%(levelname)s: %(message)s')
log.setLevel(logging.INFO)

parser = argparse.ArgumentParser("wipro crawler %s" % version)
parser.add_argument('-V', '--version',
    help='Show version', action='version',
    version='%(prog)s ')
parser.add_argument('domain', nargs='+', help='Domain(s) to crawl')
parser.add_argument('-n', '--no-download',
    help='Do not execute wget (useful for cached domains)', action='store_true')


args = parser.parse_args(sys.argv[1:])


class ParseHTML(HTMLParser):
    def __init__(self):
        super().__init__()

        self.links = []
        self.images = []

    # Handle a href and img src
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for attr in attrs:
                if attr[0] == 'href':
                    log.debug("Adding link: %s" % attr[1])
                    self.links.append(attr[1])
        if tag == "img":
            for attr in attrs:
                if attr[0] == 'src':
                    self.images.append(attr[1])
                    log.debug("Adding link: %s" % attr[1])


for domain in args.domain:
    log.info("Crawling domain %s" % domain)

    # Retrieve the website
    if not args.no_download:
        wget.append(domain)
        log.debug("wget command: %s" % " ".join(wget))
        result = subprocess.call(wget)

        if result != 0:
            raise Exception("Failed to retrieve website (see wget errors)")

    log.info("Analysing domain: %s" % domain)
    result = {}
    for root, dirs, files in os.walk(domain):
        for file in files:
            filename=join(root, file)

            log.debug("Analysing file: %s" % filename)

            with open(filename, "r") as fd:
                content_list = fd.readlines()
                content = " ".join(content_list)
                log.debug("Content of %s: %s" % (filename, content))

                parser = ParseHTML()
                parser.feed(content)

                result[filename] = { "images": parser.images, "links": parser.links }

                log.debug("Links: %s" % (" ".join(parser.links)))
                log.debug("Images: %s" % (" ".join(parser.images)))

    # Display result
    for page in result:
        images = result[page]["images"]
        links  = result[page]["links"]

        links_formatted = "\n\t\t".join(links)
        images_formatted = "\n\t\t".join(images)

        # page_info = "{name}\n\tImages:\n\t\t{images}\n\tLinks\n\t\t".format(name=page
        page_info = "{name}\n\tImages:\n\t\t{images}\n\tLinks\n\t\t{links}".format(name=page, images=images_formatted, links=links_formatted)
        print("%s" % page_info)
