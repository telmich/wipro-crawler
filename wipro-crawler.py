#!/usr/bin/env python3

import sys
import argparse
import logging
import subprocess
import os
from os.path import join
from html.parser import HTMLParser

version="0.0.1"
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

for domain in args.domain:
    log.info("Crawling domain %s" % domain)

    # Retrieve the website
    if not args.no_download:
        wget.append(domain)
        log.debug("wget command: %s" % " ".join(wget))
        result = subprocess.call(wget)

        if result != 0:
            raise Exception("Failed to retrieve website (see wget errors)")

    for root, dirs, files in os.walk(domain):
        for file in files:
            filename=join(root, file)

            log.info("Analysing file: %s" % filename)
