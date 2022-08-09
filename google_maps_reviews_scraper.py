import csv
import getopt
import json
import re
import sys
from urllib.parse import unquote
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class Scraper:
    def __init__(self, url, number_of_reviews=0):
        self.reviews_button_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div[1]/div[2]/div/div[1]/span[1]/span/span/span[2]/span[1]/button'
        self.panel_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]'
        self.url = url
        self.number_of_reviews = number_of_reviews
        self.output_file_name = None
        self.verbose = None
        self.headless = True
        self.driver = None
        self.review_id = []

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
        s = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=s, options=options)
        self.driver = driver

    def save_reviews(self, reviews):
        header = ['id', 'input_url', 'user_name', 'score', 'published_at', 'text']
        with open(self.output_file_name, 'a', newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            if reviews[0] == 1:
                writer.writerow(header)
            writer.writerow(reviews)

    def show_reviews(self, reviews):
        reviews_dict = {
            'id': reviews[0],
            'input_url': reviews[1],
            'user_name': reviews[2],
            'score': reviews[3],
            'published_at': reviews[4],
            'text': reviews[5]
        }
        print(json.dumps(reviews_dict, indent=4))

    def load_reviews(self):
        num_list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        self.driver.get(self.url)
        time.sleep(5)
        # reviews button
        reviews_button = self.driver.find_element(By.XPATH, self.reviews_button_xpath)
        review_num_text = str(reviews_button.text.split(" ")[0])
        total_number_of_reviews = ""
        for item in review_num_text:
            if item in num_list:
                total_number_of_reviews = total_number_of_reviews + item.strip()

        print(f"Total number of reviews: {total_number_of_reviews}")

        if int(total_number_of_reviews) < self.number_of_reviews:
            self.number_of_reviews = int(total_number_of_reviews)
        # clicking on reviews button
        reviews_button.click()
        time.sleep(5)
        # scrollable area
        scrollable_div = self.driver.find_element(By.XPATH, self.panel_xpath)
        # scrolling
        for i in range(0, (round(self.number_of_reviews / 10 - 1))):
            print(f"Scrolling to page {i+2}")
            self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
            time.sleep(2)
            self.get_reviews()

    def get_reviews(self):
        # getting reviews
        print("Getting reviews...")
        reviews_div = self.driver.find_elements(By.CLASS_NAME, 'jftiEf')
        for review_id, review in enumerate(reviews_div):
            try:
                more_button = review.find_element(By.CLASS_NAME, 'w8nwRe')
            except:
                more_button = None
            if more_button is not None:
                more_button.click()
            r_id = review.get_attribute('data-review-id')
            if r_id not in self.review_id:
                print(f"Review: {r_id}")
                username = review.find_element(By.CLASS_NAME, 'd4r55').find_element(By.TAG_NAME, 'span').text
                review_text = review.find_element(By.CLASS_NAME, 'MyEned').text
                rating = review.find_element(By.CLASS_NAME, 'kvMYJc').get_attribute('aria-label').strip().split(" ")[0]
                rel_date = review.find_element(By.CLASS_NAME, 'rsqaWe').text
                reviews = [review_id + 1, self.url, username, rating, rel_date, review_text]
                if self.output_file_name:
                    self.save_reviews(reviews)
                else:
                    self.show_reviews(reviews)
                self.review_id.append(r_id)


if __name__ == '__main__':
    arg_help = "{0} -u <ESTABLISHMENT_URL> -n <NUMBER_OF_REVIEWS_COLLECT> -o <FILE_NAME> -v <VERBOSE> -l <LANGUAGE>".format(sys.argv[0])
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hu:n:o:v:l:", ["help", "url=", "number_of_reviews=", "output=", "verbose=", "language="])
    except:
        print(arg_help)
        sys.exit(2)

    url, number_of_reviews_to_collect, output_file_name, verbose, language = None, None, None, None, None
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(arg_help)  # print the help message
            sys.exit(2)
        elif opt in ('-u', '--url'):
            url = arg
        elif opt in ('-n', '--number_of_reviews'):
            number_of_reviews_to_collect = arg
        elif opt in ("-o", "--output"):
            output_file_name = arg
        elif opt in ("-v", "--verbose"):
            verbose = arg
        elif opt in ("-l", "--language"):
            language = arg

    number_of_reviews_to_collect = int(number_of_reviews_to_collect)
    if language:
        url = re.sub("hl=[a-z]{2}", "", url)  # remove language parameter if present
        url = url + f"hl={language}"  # add user preferred language parameter

    url = unquote(url)  # unquote url
    print(f"url: {url}")

    scraper = Scraper(url, number_of_reviews=number_of_reviews_to_collect)
    if output_file_name:
        if '.csv' not in output_file_name:
            output_file_name = output_file_name + ".csv"
        scraper.output_file_name = output_file_name
    if verbose:
        scraper.verbose = verbose

    print("Starting scraping...")
    scraper.config_driver()
    print("Loading reviews...")
    scraper.load_reviews()
    # print("Getting reviews...")
    # scraper.get_reviews()
    scraper.driver.quit()
    print('Scraping done!')
