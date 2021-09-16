# 코알라유니브 스터디: 공공공공공경경 - 고주형
# 네이버 신지도 데이터 수집하기
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
#예외 처리 import 추가
from selenium.common.exceptions import NoSuchElementException
from pymongo import MongoClient
import requests

def init_data(region):
    client = MongoClient('localhost', 27017)
    db = client.EcoEnerge

    #pymongo 연결
    driver = webdriver.Chrome("./chromedriver")
    driver.get("https://m.map.naver.com/#/search")

    time.sleep(1)
    # 검색창에 검색어 입력하기
    search_box = driver.find_element_by_css_selector("#ct > div.search._searchView > div.Nsearch > form > div > div.Nsearch_box > div > span.Nbox_text > input")
    search_box.send_keys("{} 전기차 충전소".format(region))

    time.sleep(1)

    # 검색버튼 누르기
    search_box.send_keys(Keys.ENTER)

    # 크롤링
    time.sleep(1)
    elements = driver.find_element_by_css_selector("#ct > div.search_listview._content._ctList > ul")

    lists = elements.find_elements_by_tag_name('li')
    idx = 1
    

    for li in iter(lists):
        chargeName = li.get_attribute("data-title")
        address = driver.find_element_by_css_selector("#ct > div.search_listview._content._ctList > ul > li:nth-child({}) > div.item_info > div.item_info_inn > div > a".format(idx))
        address = address.text.split('\n')[1]
        data_entx = li.get_attribute("data-entx")
        data_enty = li.get_attribute("data-enty")
        
        
        try:
            img = driver.find_element_by_css_selector("#ct > div.search_listview._content._ctList > ul > li:nth-child({}) > div.item_info > a.item_thumb._itemThumb > img".format(idx)).get_attribute("src")
        except NoSuchElementException:
            img = None

        headers = {
            "X-NCP-APIGW-API-KEY-ID": "st5qvd1jn8",
            "X-NCP-APIGW-API-KEY": "vNwmtJeX7FNgxYnr3DhpoKjgrDptjd9gbpsyIAB5"
        }
        r = requests.get(f"https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode?query={address}", headers=headers)
        response = r.json()
        if response["status"] == "OK":
            if len(response["addresses"])>0:
                x = float(response["addresses"][0]["x"])
                y = float(response["addresses"][0]["y"])
                print(chargeName, address, img, x, y)
            doc = {
                "chargeName" : chargeName,
                "address" : address,
                "img" : img,
                "x" : x,
                "y" : y
            }
            db.chargeList.insert_one(doc)
        else:
            print( chargeName, "좌표를 찾지 못했습니다")
        idx = idx + 1
    idx = 0
    # 크롭 웹페이지를 닫음
    driver.close()

if __name__ == "__main__":
    init_data("서울")