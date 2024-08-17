import datetime
import logging
from selenium import webdriver
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def run(event, context):
    driver = webdriver.Chrome()
    # processors
    driver.get("https://techmatched.pk/product-category/processors/")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    print(soup.prettify())

    current_time = datetime.datetime.now().time()
    logger.info("Your cron function ran at " + str(current_time))
