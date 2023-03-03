import csv
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

class GoogleMapScraper:

    def __init__(self):
        # self.panel_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]'
        self.panel_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]'
        self.business_list = []
        self.business_info = {}
        # self.number_of_reviews = number_of_reviews
        self.output_file_name = "google_map_business_nashville.csv"
        self.verbose = None
        self.headless = False
        self.driver = None
        self.d_id = 0
        self.unique_check = []


    def config_driver(self):
        options = webdriver.ChromeOptions()
        # options.add_argument("--lang=fr")
        if self.verbose:
            if "headless" in self.verbose:
                headless = str(self.verbose.split("=")[-1]).strip().lower()
                if headless == "false":
                    self.headless = False
        if self.headless:
            options.add_argument("--headless")
        # s = Service(ChromeDriverManager().install())
        # driver = webdriver.Chrome(service=s, options=options)
        driver = webdriver.Chrome(executable_path="/Users/tohfaakib/.wdm/drivers/chromedriver/mac_arm64/108.0.5359/chromedriver", options=options)
        self.driver = driver

    def save_data(self, data):
        header = ['id', 'company_name', 'rating', 'reviews_count', 'address', 'category', 'phone', 'website']
        with open(self.output_file_name, 'a', newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            if data[0] == 1:
                writer.writerow(header)
            writer.writerow(data)

    def get_business_info(self):
        time.sleep(2)
        for business in self.driver.find_elements(By.CLASS_NAME, 'THOPZb'):
            try:
                name = business.find_element(By.CLASS_NAME, 'fontHeadlineSmall').find_element(By.TAG_NAME, 'span').text
            except:
                name = ''

            try:
                reviews_block = business.find_element(By.CLASS_NAME, 'AJB7ye').text.split("(")
                rating = reviews_block[0].strip()
                reviews_count = reviews_block[1].split(")")[0].strip()
            except:
                rating = ""
                reviews_count = ""

            try:
                address_block = business.find_elements(By.CLASS_NAME, "W4Efsd")[2].text.split("·")
                if len(address_block) >= 2:
                    address = address_block[1].strip()
                    category = address_block[0].strip()
                elif len(address_block) == 1:
                    address = ""
                    category = address_block[0]
            except:
                address = ""
                category = ""
            try:
                contact = business.find_elements(By.CLASS_NAME, "W4Efsd")[3].text.split("·")[-1].strip()
            except:
                contact = ""

            if "+1" not in contact:
                try:
                    contact = business.find_elements(By.CLASS_NAME, "W4Efsd")[4].text.split("·")[-1].strip()
                except:
                    contact = ""

            try:
                website = business.find_element(By.CLASS_NAME, "lcr4fd").get_attribute("href")
            except:
                website = ""

            unique_id = "".join([name, rating, reviews_count, address, category, contact, website])
            if unique_id not in self.unique_check:
                self.d_id += 1
                data = [self.d_id, name, rating, reviews_count, address, category, contact, website]
                print(data)
                self.save_data(data)
                self.unique_check.append(unique_id)

    def load_companies(self, url):
        print("Getting business info", url)
        self.driver.get(url)
        time.sleep(5)
        scrollable_div = self.driver.find_element(By.XPATH, self.panel_xpath)
        # scrolling
        flag = True
        i = 0
        while flag:
            print(f"Scrolling to page {i + 2}")
            self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
            time.sleep(2)

            if "You've reached the end of the list." in self.driver.page_source:
                flag = False

            self.get_business_info()
            i += 1



urls = [
    "https://www.google.com/maps/search/Nashville+Concrete+contractor/@35.5202604,-87.8699961,8z",
    "https://www.google.com/maps/search/Nashville+Masonry+contractor/@35.5098836,-87.8700415,8z/data=!3m1!4b1"
]

BusinessScraper = GoogleMapScraper()
BusinessScraper.config_driver()
for url in urls:
    print(url)
    # BusinessScraper.get_business_info(url)
    BusinessScraper.load_companies(url)
print(BusinessScraper.business_info)