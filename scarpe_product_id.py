import undetected_chromedriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as ExpectedConditions
import pandas as pd
import time
from fake_useragent import UserAgent
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

def get_url(search_term):
    template = 'https://www.amazon.com/s?k={}'
    search_term = search_term.replace(' ', '+')
    url = template.format(search_term)
    return url

def scrape_records(item):
    result = item['data-asin']
    return result

def scrape_amazon(search_term):
    ua = UserAgent()
    options = Options()
    options.add_argument(f"user-agent={ua.random}")
    driver = undetected_chromedriver.Chrome(options=options)
    url = get_url(search_term)
    driver.get(url)
    time.sleep(5)
    records = []
    while True:
        time.sleep(5)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        results = soup.find_all('div', {'data-component-type': 's-search-result'})

        for item in results:
            try:
                record = scrape_records(item)
                records.append(record)
            except Exception as e:
                print(f"Error scraping item: {e}")
        try:
            nextButton = driver.find_element(By.XPATH, '//a[text()="Next"]')
            driver.execute_script("arguments[0].scrollIntoView();", nextButton)
            WebDriverWait(driver, 200).until(ExpectedConditions.element_to_be_clickable(nextButton))
            nextButton.click()
        except NoSuchElementException:
            print("Breaking as Last page Reached")
            break

    driver.close()
    df = pd.DataFrame(records, columns=['id_product'])
    return df

search_term = 'drink glasses'
df = scrape_amazon(search_term)
df.to_csv('drink_glasses_product_id.csv',index = False)