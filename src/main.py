#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
# Check the python version. If the python version is 2, print message and exit.
if sys.version_info[0] < 3:
    print ("This program requires Python 3")
    exit()

# Import scraper class
from scraper import CarrerasScraper

# Scraper creation
scraper = CarrerasScraper();

# Initiates scraping process and stores the results
scraper.scrape();
