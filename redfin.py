import json
import logging
from bs4 import BeautifulSoup
from parser import RedfinPageParser, RedfinDownloadParser
from redfin_request import RedfinRequest

class Redfin():
    def __init__(self, redfin_request=RedfinRequest(False)):
        self.sold_houses = []
        self.request = redfin_request
        

    def search_sold_houses(self):
        """
        Get the list of all the city from the homepage
        """
        self.sold_houses = []

        logging.info('start loading \"www.redfin.com\".')

        main_page_source = self.request.make_page_request("https://www.redfin.com")

        logging.info('parsing city list...')

        city_hrefs = self.parse_city_list(main_page_source)
        for city_href in city_hrefs:
            self.search_sold_houses_area(city_href)

    def search_sold_houses_area(self, area_str: str):
        area_str = area_str.strip('/')

        start_url = '/'.join(['https://www.redfin.com', area_str, 'recently-sold'])

        logging.info('querying {} using download link.'.format(start_url))

        # To search the cvs file
        download_parser = RedfinDownloadParser(start_url)
        sold_houses = download_parser.parse()
        if sold_houses is not None:
            self.sold_houses += sold_houses
        else:
            logging.info("querying city {} failed. we use another solution.".format(start_url))
            # there is no cvs file, parse the html page
            page_parser = RedfinPageParser(start_url)
            sold_houses = page_parser.parse()
            if sold_houses is not None:
                self.sold_houses = self.sold_houses + sold_houses
            else:
                logging.error("page {} parser error occur.".format(start_url))

    def parse_city_list(self, page_source: str):
        soup = BeautifulSoup(page_source, 'html.parser')
        ul = soup.find('ul', {'class': 'city-list'})

        city_list = []
        for li in ul.findAll('li', {'class': 'city'}):
            city_list.append(li.find('a').attrs["href"])

        logging.info("found {} cities.".format(len(city_list)))
        return city_list

    def output(self):
        output_list = []

        if self.sold_houses:
            for house in self.sold_houses:
                output_list.append(house.as_dict())

            with open('output_file.json', 'w') as f:
                json.dump(output_list, f)
        else:
            logging.info('no appropriate data to output.')


