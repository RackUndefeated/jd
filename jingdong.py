
import pymongo
from config import *

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq

client = pymongo.MongoClient(MONGO_URL,27017)
db = client.MONGO_DB


driver = webdriver.Chrome()
wait = WebDriverWait(driver,10)


def search():
    try:
        driver.get(URL)
        driver.maximize_window()
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#key')))
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#search > div > div.form > button')))
        input.send_keys(KEYWORD)
        submit.click()
        pages = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#J_bottomPage > span.p-skip > em:nth-child(1)')))
        get_book()
        return pages.text
    except TimeoutException:
        search()

def next_page(page):
    try:
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#J_bottomPage > span.p-skip > input')))
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#J_bottomPage > span.p-skip > a')))
        input.clear()
        input.send_keys(page)
        submit.click()
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#J_bottomPage > span.p-num > a.curr')))
    except TimeoutException:
        next_page(page)

def get_book():
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#J_goodsList > ul > li')))
    html = driver.page_source
    doc = pq(html)
    book_list = doc('#J_goodsList .gl-warp .gl-item').items()
    for book in  book_list:
        product = {
            'name':book.find('.p-name em').text(),
            'publish':book.find('.p-shopnum a').text(),
            'price':book.find('.p-price strong').text()
        }
        print(product)
        to_mongodb(product)

def to_mongodb(result):
    try:
        if db[MONGO_TABLE].insert(result):
            print('存储成功！')
    except Exception:
        print('存储失败！')

def run():
    search()
    for i in range(2,PAGES):
         next_page(i)
    driver.close()



if __name__ == '__main__':
    run()
