import re
import random
from time import sleep
from requests import request
from parsel import Selector


from log import logger

INFORMATION = {
                'title': '//h1[@class="head"]/text()',
                'mileage': '//div[@class="mb-10 bold dhide"]/text()',
                'username': '//h4[@class="seller_info_name bold"]/text()',
                'img_url': '//img[@class="outline m-auto"]/@src',
                'car_number': '//span[@class="state-num ua"]/text()',
                'car_vin_code': '//span[@class="vin-code"]/text()',
                'img_total_count': '//span[@class="count"]/span[@class="dhide"]/text()',
                'phone_number': '//span/@data-phone-number',
                'usd_price': '//span[@class="price_value bold"]/text()'
            }

EXCEPT = ['car_number', 'car_vin_code']


class Scraper:

    HEADERS = {"Accept": "*/*",
               "User-Agent": "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) "
               "Version/11.0 Mobile/15A5341f Safari/604.1"}

    def __init__(self):
        self.url = 'https://auto.ria.com/uk/legkovie/?page='


    def request_handler(self, url: str):
        response = request(method='GET', url=url, headers=self.HEADERS)
        count = 0
        while count < 5:
            if response.status_code == 200:
                return Selector(text=response.text)
            else:
                logger.info(f'попытка соединения № {count+1} не удалась ')
                count += 1
        logger.error("Не удалось установить соединение по указанному URL")

    def get_cars_links(self, number: int) -> list:
        all_links = []
        for i in range(number):
            url = self.url + str(i+1)
            try:
                tree = self.request_handler(url)
                links = tree.xpath('//div[@class="content-bar"]/a/@href').extract()
                for link in links:
                    all_links.append(link)
                logger.info(f'созданы ссылки для результатов поиска на {i + 1} странице')
                sleep(random.randrange(2, 4))
            except AttributeError:
                logger.error("Отсутствует информация для обработки, проверьте правильность URL, XPATH")
        if all_links:
            logger.info('создание ссылок для работы с карточками по поиску б/у легковые машины завершено')
            return all_links
        raise SystemExit

    @staticmethod
    def converter_in_int(information: dict) -> dict:
        for key, value in information.items():
            if key == 'img_total_count' or key == 'phone_number' or key == 'usd_price':
                information[key] = int(re.sub("[^0-9]", '', value))
        return information

    @staticmethod
    def execute(information: dict, tree) -> dict:
        converter_information = {}
        try:
            for key, value in information.items():
                converter_information[key] = tree.xpath(value).extract_first()
        except AttributeError:
            logger.error("Отсутствует информация для обработки, проверьте правильность URL, XPATH")
        return converter_information

    @staticmethod
    def validator_none(information: dict) -> bool:
        result = True
        for key, value in information.items():
            if value is None and key not in EXCEPT:
                result = False
                logger.warning("Карточка машины не содержит всех данных")
                break
        return result

    def get_information_about_cars(self, url) -> dict or None:
        tree = self.request_handler(url)
        information = self.execute(INFORMATION, tree)
        information['url'] = url
        validation = self.validator_none(information)
        if validation:
            information = Scraper.converter_in_int(information)
            return information
        else:
            return None



