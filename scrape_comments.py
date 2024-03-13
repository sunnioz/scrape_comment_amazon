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

def get_url(id_product,star):
    template = 'https://www.amazon.com/product-reviews/{}/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&filterByStar={}_star&reviewerType=all_reviews&sortBy=recent&pageNumber=1'
    url = template.format(id_product,star)
    return url

def read_csv_file(file_path):
    df = pd.read_csv(file_path)
    id_products = df['id_product'].tolist()
    
    return id_products

data_list = read_csv_file('drink_glasses_product_id.csv')

def scrape_records(item):
    overview_guest = item.find('a',attrs = {'data-hook':'review-title'})
    overview_rating = overview_guest.find('span',attrs = {'class':'a-icon-alt'})
    if overview_rating:
        overview_rating = overview_rating.text
    overview_text = overview_guest.find_all('span')[-1]
    if overview_text:
        overview_text = overview_text.text
    comment = item.find('span',attrs= {'data-hook':'review-body'})
    if comment:
        comment = comment.span.text
    name_guest = item.find('span',attrs = {'class':'a-profile-name'})
    if name_guest:
        name_guest = name_guest.text
    date_review = item.find('span',attrs = {'data-hook':'review-date'})
    if date_review:
        date_review = date_review.text
    result = (name_guest,date_review,overview_rating,overview_text, comment)
    return result


def scrape_amazon(search_term,star,driver):
    url = get_url(search_term,star)
    driver.get(url)
    time.sleep(2)
    records = []
    while True:
        # Scroll to the bottom of the page to load more items
        # Add a short delay to let the page load
        time.sleep(10)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        results = soup.find_all('div', {'data-hook': 'review'})

        for item in results:
            try:
                record = scrape_records(item)
                records.append(record)
            except Exception as e:
                print(f"Error scraping item: {e}")

        # Check if there is a "Next" button on the page
        try:
            nextButton = driver.find_element(By.XPATH, '//a[text()="Next page"]')
            driver.execute_script("arguments[0].scrollIntoView();", nextButton)
            WebDriverWait(driver, 300).until(ExpectedConditions.element_to_be_clickable(nextButton))
            nextButton.click()
        except NoSuchElementException:
            print("Breaking as Last page Reached")
            break


    df = pd.DataFrame(records, columns=['name_guest','date_review','overview_rating','overview_text', 'comment'])
    return df

df_h = pd.DataFrame(columns=['name_guest', 'date_review', 'overview_rating', 'overview_text', 'comment'])
df_h.to_csv('data.csv', index=False)
star = 'one'
# ua = UserAgent()
# options = Options()
# options.add_argument(f"user-agent={ua.random}")
driver = undetected_chromedriver.Chrome()
for id_product in data_list:
    df = scrape_amazon(id_product,star,driver)
    print("success! {}".format(id_product))
    df.to_csv('data_comment.csv',mode = 'a',header= False,index = False)
driver.close()