import time
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from database import Database
from scraper import Scraper


class SeleniumScraper:
    url = 'https://auto.ria.com/uk/legkovie/?page='
    xpath = '//a[@class="address"]'
    xpath_cookies = '//div[@class="c-notifier-btns"]/label[@class="js-close c-notifier-btn"]'

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.scrap = Scraper()
        self.data_base = Database()
        self.actions = ActionChains(self.driver)

    def get_car_information(self, element: object, url: str) -> dict:
        time.sleep(2)
        self.actions.move_to_element(element).perform()
        time.sleep(2)
        self.actions.key_down(Keys.CONTROL).click(element).key_up(Keys.CONTROL).perform()
        time.sleep(2)
        self.driver.switch_to.window(self.driver.window_handles[-1])
        time.sleep(3)
        car_information = self.scrap.get_information_about_cars(url)
        time.sleep(5)
        self.driver.close()
        time.sleep(4)
        self.driver.switch_to.window(self.driver.window_handles[0])
        time.sleep(2)
        if car_information:
            return car_information

    def walker(self, pagination: int) -> list:
        page = 1
        cars = []
        self.driver.get(self.get_url(self.url, page))
        time.sleep(2)
        accept = self.driver.find_element(By.XPATH, self.xpath_cookies)
        accept.click()
        try:
            while pagination > 0:
                pagination -= 1
                elements = self.driver.find_elements(By.XPATH, self.xpath)
                links = [i.get_attribute('href') for i in elements]
                time.sleep(2)
                for i in range(len(elements)):
                    try:
                        cars_info = self.get_car_information(elements[i], links[i])
                        if cars_info:
                            cars.append(cars_info)
                    except Exception:
                        continue
                if pagination > 0:
                    page += 1
                    self.paginator(self.get_url(self.url, page))
        except Exception:
            pass
        finally:
            self.driver.close()
            self.driver.quit()
            return cars

    def paginator(self, url) -> None:
        print(url)
        self.driver.switch_to.window(self.driver.window_handles[0])
        time.sleep(5)
        next_page = self.driver.find_elements(By.XPATH, f"//a[@href='{url}']")
        time.sleep(2)
        self.actions.move_to_element(next_page[1]).perform()
        time.sleep(2)
        next_page[1].click()
        time.sleep(5)

    def get_url(self, url: str, page: int) -> str:
        url_next = url + f'{page}'
        return url_next

    def main(self, pagination: int):
        self.data_base.create_table()
        car_info = self.walker(pagination)
        self.data_base.insert_car_info(car_info)
        self.data_base.cursor.close()
        self.data_base.connection.close()


if __name__ == '__main__':
    start = SeleniumScraper()
    start.main(2)
