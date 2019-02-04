# Redfin Crawler

a scraper for Redfin.com using Python3 for relevant real estate information for recently sold homes.


## Methodology

### Block Protect
Three methods are introduced to prevent getting blacklisted while scraping.

1. random sleep
2. random User-Agent
3. using different proxies

### Parser tools

1. RedfinDownloadParser: parse the cvs download from the page. if it exists, download and parse, otherwise, return fail.
2. RedfinPageParser: if the cvs isn't provided, the html page will be parsed. And should handle multiple pages.


### TODO:

1. Modular
2. Request response for different HTTP Code
3. Test
4. SQL persistants