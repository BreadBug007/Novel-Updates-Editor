from selenium import webdriver
import requests
from bs4 import BeautifulSoup as bs
from time import sleep
import os
import sys


def site_login():
    chrome.get("https://www.novelupdates.com/login/")
    sleep(3)
    try:
        chrome.find_element_by_class_name("qc-cmp-button").click()
    except Exception as e:
        print("No 'Privacy and cookie policy message' ")
        print(e)
        pass
    sleep(2)
    chrome.find_element_by_id("user_login").send_keys(username)
    chrome.find_element_by_id("user_pass").send_keys(password)
    chrome.find_element_by_id("wp-submit").click()
    sleep(1)


def find_page(first_chap, input_chap):
    pg = int((int(first_chap[1:]) - int(input_chap)) / 15)
    return pg + 1


def get_group(url):
    button = chrome.find_element_by_css_selector("i.fa.fa-filter.chp")
    chrome.execute_script("arguments[0].scrollIntoView();", button)
    button.click()
    sleep(2)

    table = chrome.find_element_by_css_selector("ol.sp_grouptable")
    entries = table.find_elements_by_class_name("grp-filter-attr")

    page_dict = {}

    for entry in entries:
        group_id = entry.get_attribute("value")
        try:
            grp_url = url + "?grp={}".format(group_id)
            with requests.Session() as s:
                source = s.get(grp_url)
            soup = bs(source.content, 'lxml')
            soup = soup.find('div', class_="digg_pagination")
            pages = soup.find_all("a")
            page_count = int(pages[-2].text)
            page_dict[group_id] = page_count
        except Exception as e:
            pass

    return max(page_dict, key=page_dict.get)


def search_novel(search_term):
    url = "https://www.novelupdates.com/?s={}&post_type=seriesplans".format(search_term)
    chrome.get(url)
    chrome.find_element_by_css_selector("span.w-blog-entry-title-h.entry-title").click()
    return chrome.current_url


def edit(url, input_chap):
    group_id = get_group(url)
    new_url = url + "?grp={}".format(group_id)

    with requests.Session() as s:
        source = s.get(new_url)

    soup = bs(source.text, 'lxml')
    first_chap = soup.find('a', class_='chp-release').text
    search_page = find_page(first_chap, input_chap)

    if search_page == 0:
        print("Chapter not available")
        return

    search_url = url + "?pg=" + str(search_page) + "&grp={}".format(group_id)

    chrome.get(search_url)
    sleep(2)

    table = chrome.find_element_by_css_selector('#myTable')
    chapters = table.find_elements_by_xpath('.//tr')

    for chapter in chapters[1:]:
        try:
            check_conditions = chapter.find_element_by_css_selector("label.enableread")
            chap_no = chapter.find_element_by_class_name("chp-release").text

            if chap_no[1:] == input_chap:
                chrome.execute_script("arguments[0].click();", check_conditions)
                print("Chapter found and checked")
                sleep(5)
                return
        except Exception as e:
            print(e)


scriptname, username, password, *novel_name, chapter = tuple(sys.argv)


if scriptname == os.path.basename(__file__):

    chromeOptions = webdriver.ChromeOptions()
    prefs = {'profile.managed_default_content_settings.images': 2, 'disk-cache-size': 4096}
    chromeOptions.add_experimental_option("prefs", prefs)

    with webdriver.Chrome(options=chromeOptions) as chrome:

        site_login()
        sleep(1)

        novel_name = novel_name[0]
        url = search_novel(novel_name)
        edit(url, chapter)
