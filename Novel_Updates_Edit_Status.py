from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import requests
from bs4 import BeautifulSoup as bs
import os
import sys
from time import sleep


def site_login():
    chrome.get("https://www.novelupdates.com/login/")
    wait = WebDriverWait(chrome, 5)
    try:
        wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "qc-cmp-button"))).click()
    except TimeoutException:
        print("Page taking too long to load or no privacy and cookie policy message")
    chrome.find_element_by_id("user_login").send_keys(username)
    chrome.find_element_by_id("user_pass").send_keys(password)
    wait.until(EC.presence_of_element_located((By.ID, "wp-submit"))).click()


def find_page(url, first_chap, input_chap):
    first_chap = int(first_chap[1:])
    input_chap = int(input_chap)
    if input_chap > first_chap:
        print("Chapter not released yet")
        return
    page = int((first_chap - input_chap) / 15) + 1
    last_page = get_last_page(url)
    page_range = [i for i in range(page, last_page + 1)]
    for page in page_range:
        check_url = url + "?pg={}".format(page)
        if check_page(check_url, input_chap):
            return page


def check_page(url, input_chap):
    with requests.Session() as s:
        source = s.get(url)
    soup = bs(source.content, 'lxml')
    pages = soup.find_all('a', class_="chp-release")
    for page in pages:
        if int(page.text[1:]) == input_chap:
            return True
    return False


def search_novel(search_term):
    url = "https://www.novelupdates.com/?s={}&post_type=seriesplans".format(search_term)
    chrome.get(url)
    wait = WebDriverWait(chrome, 5)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"span.w-blog-entry-title-h.entry-title"))).click()
    return chrome.current_url


def get_last_page(url):
    with requests.Session() as s:
        source = s.get(url)
    soup = bs(source.content, 'lxml')
    soup = soup.find('div', class_="digg_pagination")
    pages = soup.find_all("a")
    last_page = int(pages[-2].text)
    return last_page


def edit_status(url, input_chap):
    with requests.Session() as s:
        source = s.get(url)
    soup = bs(source.text, 'lxml')
    first_chap = soup.find('a', class_='chp-release').text
    search_page = find_page(url, first_chap, input_chap)
    novel_title = soup.find('div', class_="seriestitlenu").text

    if search_page is None:
        return

    search_url = url + "?pg={}".format(search_page)

    chrome.get(search_url)

    table = WebDriverWait(chrome, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#myTable")))
    chapters = table.find_elements_by_xpath('.//tr')

    for chapter in chapters[1:]:
        try:
            check_conditions = chapter.find_element_by_css_selector("label.enableread")
            chap_no = chapter.find_element_by_class_name("chp-release").text

            if chap_no[1:] == input_chap:
                chrome.execute_script("arguments[0].click();", check_conditions)
                print("Chapter {} for {} found and checked".format(input_chap, novel_title))
                sleep(3)
                return
        except Exception as e:
            print(e)


scriptname, username, password, *novel_name, chapter = tuple(sys.argv)

if scriptname == os.path.basename(__file__):

    chromeOptions = webdriver.ChromeOptions()
    prefs = {'profile.managed_default_content_settings.images': 2}
    chromeOptions.add_experimental_option("prefs", prefs)

    with webdriver.Chrome(options=chromeOptions) as chrome:

        site_login()
        novel_name = novel_name[0]
        url = search_novel(novel_name)
        edit_status(url, chapter)


