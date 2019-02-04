'''
Parser tools
1. RedfinDownloadParser: parse the cvs download from the page.
if it exists, download and parse, otherwise, return fail.
2. RedfinPageParser: if the cvs isn't provided, the html page will be parsed. 
And should handle multiple pages.
'''

import csv
import json
import logging
from io import StringIO
# from typing import List

from bs4 import BeautifulSoup

from house import House
from redfin_request import RedfinRequest

_REDFIN_PREFIX = 'https://www.redfin.com'
_REDFIN_SUFFIX = 'recently-sold'
_REQUEST_HEADER = {
    'User-Agent':
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64',
    'Accept':
        'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset':
        'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Language':
        'en-US,en;q=0.8',
    'Connection':
        'keep-alive'
}


class RedfinDownloadParser(object):
    """
    Parse the downlowned csv file
    """
    def __init__(self, redfin_page_url, redfin_request = RedfinRequest(False)):
        self.redfin_page_url = redfin_page_url
        self.redfin_request = redfin_request

    def parse(self):
        redfin_page_source = self.redfin_request.make_page_request(self.redfin_page_url)
        soup = BeautifulSoup(redfin_page_source, 'html.parser')

        try:
            download_save = soup.find('div', {"class": "DownloadAndSave"})
            download_save_href = download_save.find('a', {"id": "download-and-save"}).attrs['href']

            download_csv = self.download_houses_info(download_save_href)
            return self.parse_csv(download_csv)
        except:
            logging.error("cannot find download area.")
            return None

    def download_houses_info(self, download_link: str):
        '''
        get linked csv content
        '''
        if not download_link.startswith(_REDFIN_PREFIX):
            download_link = '/'.join([_REDFIN_PREFIX, download_link])
        return self.redfin_request.make_page_request(download_link)

    def parse_csv(self, sold_houses_content):
        '''
        extract house model from csv.
        '''
        all_sold_houses = []

        f = StringIO(sold_houses_content)
        reader = csv.DictReader(f)

        for row in reader:
            house_info = {
                # Address
                "street_address": row["ADDRESS"] if "ADDRESS" in row else 'N/A',
                "city": row["CITY"] if 'CITY' in row else 'N/A',
                "state": row["STATE"] if "STATE" in row else 'N/A',
                # rooms
                "beds": row["BEDS"] if "BEDS" in row else 'N/A',
                "baths": row["BATHS"] if "BATHS" in row else 'N/A',
                "sq_ft": row["SQUARE FEET"] if "SQUARE FEET" in row else 'N/A',
                # info
                "sold_price": row["PRICE"] if "PRICE" in row else 'N/A',
                "year_built": row["YEAR BUILT"] if "YEAR BUIL" in row else 'N/A',
                "property_type": row["PROPERTY TYPE"] if "PROPERTY TYPE" in row else 'N/A',
                # years on market
                "days_on_market": row["DAYS ON MARKET"] if "DAYS ON MARKET" in row else 'N/A'
            }

            house = House.from_dict(house_info)
            all_sold_houses.append(house)
        return all_sold_houses


class RedfinPageParser(object):
    """
    Parse the html pages to get the info of each house
    """
    def __init__(self, redfin_page_url, redfin_request = RedfinRequest(False)):
        self.related_pages = []
        self.sold_houses = []
        self.redfin_page_url = redfin_page_url
        self.redfin_request = redfin_request

    def parse(self):
        try:
            page_source = self.redfin_request.make_page_request(self.redfin_page_url)
        except:
            logging.error('request page {} failed.'.format(self.redfin_page_url))
            return

        # generate the list of links of other pages, the rule is: page-1, page-2...
        self.parse_related_pages(page_source)

        sold_houses = self.parse_single_page(page_source)
        self.sold_houses += sold_houses

        # if there are other pages, also should parse other pages
        if len(self.related_pages) != 0:
            self.handle_related_pages()
            return

        return self.sold_houses

    def parse_single_page(self, page_source):
        '''
        Parse the current page, to get the inform of houses
        '''
        soup = BeautifulSoup(page_source, 'html.parser')

        all_sold_houses = []

        # Every Home Card contains home info.
        # Price. Address. Type.
        sold_houses_info = soup.find_all('div', attrs={"class": "HomeCardContainer"})

        for sold_house in sold_houses_info:
            house_json = {}

            # home stat. Beds. Baths
            try:
                # May V1 or V2
                home_stat = sold_house.find('div', {"class": "HomeStats font-size-smaller"})
                if home_stat is None:
                    home_stat = sold_house.find('div', {"class": "HomeStatsV2 font-size-small"})
                    self.parse_home_stat2_v2(home_stat, house_json)
                else:
                    self.parse_home_stats_v1(home_stat, house_json)
            except:
                print("parse home stat failed.")
                house_json['beds'] = 'N/A'
                house_json['baths'] = 'N/A'
                house_json['sq_ft'] = 'N/A'

            sold_house_address = sold_house.find('script')
            self.parse_house_address(sold_house_address, house_json)

            # price
            try:
                price = sold_house.find('span', {"class": "homecardPrice font-size-small font-weight-bold"})
                if price is None:
                    price = sold_house.find('span', {"class": "homecardV2Price"})
                house_json['sold_price'] = price.text[1:].replace(',', '')
            except:
                print('parse house price failed.')
                house_json['sold_price'] = 'N/A'

            # # sold time.
            # try:
            #     sold_time = sold_house.find('span', {'class': 'HomeSash font-weight-bold roundedCorners'})
            #     house_json['sold_price'] = sold_time.text
            # except:
            #     house_json['sold_price'] = 'N/A'

            house_json['year_built'] = 'N/A'
            house_json['days_on_market'] = 'N/A'

            house = House.from_dict(house_json)
            all_sold_houses.append(house)
        return all_sold_houses

    def parse_related_pages(self, page_source):
        '''
        :param page_source: 需要解析的页面内容
        '''
        soup = BeautifulSoup(page_source, 'html.parser')

        try:
            paging_control = soup.find('div', {'class': 'PagingControls'})
            if paging_control is not None:
                last_url = paging_control.findAll('a')[-1].attrs['href']
                last_url = _REDFIN_PREFIX + last_url
                # template and max page count => generate all pages without current page.
                page_template_elem = last_url.split('-')
                pages_count = int(page_template_elem[-1])
                last_url_template = last_url.replace(page_template_elem[-1], '')

                # generate the list of links of each page
                for page_index in range(1,pages_count):
                    page_url = '{}{}'.format(last_url_template, page_index)
                    if page_index == 1:
                        page_url = page_url.replace('/page-1', '')
                    if page_url == self.redfin_page_url:
                        continue
                    self.related_pages.append(page_url)
            else:
                # Found no related pages.
                self.related_pages = []
        except:
            logging.debug('not found paging control.')

    def handle_related_pages(self):
        for page_url in self.related_pages:
            self.parse_single_page(self.redfin_request.make_page_request(page_url))
            self.related_pages.remove(page_url)

    def parse_home_stats_v1(self, home_stat_source, output: dict):
        '''
        parse home stat, for example: Beds, Baths, Sq. Ft.
        return dictionary { Beds: xxx, Baths: xxx, sq_ft:xxx }
        '''
        home_stat = {}
        for home_stat_property in home_stat_source.find_all('div', recursive=False):
            # data-rf-test-name="homecardLabel"
            stat_key = home_stat_property.find('div', attrs={"data-rf-test-name": "homecardLabel"}).text
            stat_value = home_stat_property.find('div', attrs={"class": "value"}).text
            home_stat[stat_key] = stat_value

        # Beds, Baths, Sq. Ft.
        output['beds'] = home_stat['Beds']
        output['baths'] = home_stat['Baths']
        output['sq_ft'] = home_stat['Sq. Ft.']

    def parse_home_stat2_v2(self, home_stat_source, output: dict):
        for home_stat_property in home_stat_source.find_all('div', {'class': 'stats'}, recursive=False):
            if "Beds" in home_stat_property.text:
                output['beds'] = home_stat_property.text.replace('Beds', '').replace(' ', '')
            if "Baths" in home_stat_property.text:
                output["baths"] = home_stat_property.text.replace('Baths', '').replace(' ', '')
            if "Sq. Ft." in home_stat_property.text:
                output['sq_ft'] = home_stat_property.text.replace('Sq. Ft.', '').replace(',', '').replace(' ', '')

    def parse_house_address(self, house_address_source, output: dict):
        house_address_source = house_address_source.text.strip()
        details = json.loads(house_address_source)

        if isinstance(details, list):
            details = details[0]

        # property_type
        try:
            output['property_type'] = details['@type']
        except:
            output['property_type'] = 'N/A'

        # street address
        try:
            output['street_address'] = details['address']['streetAddress']
        except:
            output['street_address'] = 'N/A'

        # state
        try:
            output['state'] = details['address']['addressRegion']
        except:
            output['state'] = 'N/A'

        # not in ld+/json
        output['city'] = 'N/A'

        # {'@type': 'PostalAddress',
        #  'streetAddress': '1310 W 16th St',
        #  'addressLocality': 'Little Rock',
        #  'addressRegion': 'AR',
        #  'postalCode': '72202',
        #  'addressCountry': 'US'}
