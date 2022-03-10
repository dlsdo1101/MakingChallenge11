# selenium import 부분
import selenium
from selenium import webdriver
from selenium.webdriver import ActionChains

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
import time


#mongoDB 저장 패키지
from pymongo import MongoClient
client = MongoClient('localhost',27017)
db = client.exhibition_project

# 같은 폴더에서 크롬드라이버 불러오기
driver = webdriver.Chrome('chromedriver_window')


# 전시 분야 제외 이외 분야에서 추가
class_url_list = [{'class':'museum' , 'url':'http://ticket.interpark.com/TPGoodsList.asp?Ca=Eve&SubCa=Eve_M'},
                  {'class':'event/festival','url':'http://ticket.interpark.com/TPGoodsList.asp?Ca=Eve&SubCa=Eve_C'},
             {'class':'childs_experience' , 'url':'http://ticket.interpark.com/TPGoodsList.asp?Ca=Eve&SubCa=Eve_X'},
             {'class':'class' , 'url':'http://ticket.interpark.com/TPGoodsList.asp?Ca=Eve&SubCa=Eve_S'}]

for class_url in class_url_list:

    # 인터파크 전시회 검색결과 띄우기
    driver.get(url=class_url['url'])
    # 해당 페이지가 전부 로드될 때 까지 대기
    time.sleep(1)


    divs = []
    divs = driver.find_elements(by=By.CSS_SELECTOR, value='body > table > tbody > tr:nth-child(2) > td:nth-child(3) > div > div > div.con > div > table > tbody > tr')
    for i in range(len(divs)):
        # 인터파크 전시회 검색 결과에서 크롤링 (1차)
        div = driver.find_element(by=By.CSS_SELECTOR, value= f'body > table > tbody > tr:nth-child(2) > td:nth-child(3) > div > div > div.con > div > table > tbody > tr:nth-child({i+1})')
        a_title = div.find_element(by=By.CSS_SELECTOR, value='td.RKtxt > span > a').text

        Cheak_DB_in = list(db.exhibition_info.find({'title':a_title},{'_id':False}))
        if not Cheak_DB_in:

            a_ticket_link = div.find_element(by=By.CSS_SELECTOR, value='td.RKtxt > span > a').get_attribute("href")
            a_image_link = div.find_element(by=By.CSS_SELECTOR, value='td.RKthumb > a > img').get_attribute("src")
            a_place = div.find_element(by=By.CSS_SELECTOR, value='td:nth-child(3) > a').text
            a_place_link = div.find_element(by=By.CSS_SELECTOR, value='td:nth-child(3) > a').get_attribute("href")

            a_period = div.find_element(by=By.CSS_SELECTOR, value='td:nth-child(4)').text
            a_start_date = a_period.split('~')[0]
            a_end_date = a_period.split('~')[1].strip('\n')

            a_class = [ class_url['class'] ]

            # 1차 크롤링 결과 print
            print(a_title + '/' + a_ticket_link)
            print('장소: '+a_place + '/' + a_place_link)
            print('시작날짜: ' + a_start_date + ' /종료날짜: ' + a_end_date)
            print('구분: ' + a_class[0] + ' 이미지링크: ' +  a_image_link)


            # 전시회 예매 페이지로 이동
            div.find_element(by=By.CSS_SELECTOR, value='td.RKtxt > span > a').click()
            time.sleep(2)

            # 연령제한 / 가격 크롤링 (2차)
            a_age_limit = ''
            info_list_tag = driver.find_elements(by=By.CLASS_NAME, value='infoItem')
            for info in info_list_tag:
                if info.find_element(by=By.CSS_SELECTOR, value='strong').text == '관람연령':
                    a_age_limit = info.find_element(by=By.CSS_SELECTOR, value='div > p').text

            a_price = ''
            price_cheak = []
            price_cheak = driver.find_elements(by=By.CLASS_NAME, value='infoPriceList')
            if price_cheak:
                price_list_tag = driver.find_element(by=By.CLASS_NAME, value='infoPriceList')
                price_list = price_list_tag.find_elements(by=By.CLASS_NAME, value='price')
                sale_list = price_list_tag.find_elements(by=By.CLASS_NAME, value='sale')
                price_etc_list = driver.find_elements(by=By.CSS_SELECTOR, value='#container > div.contents > div.productWrapper > div.productMain > div.productMainTop > div > div.summaryBody > ul > li.infoItem.infoPrice > div > ul > li:nth-child(2) > div > div > ul > li:nth-child(1) > strong')
                price_etc_list2 = driver.find_elements(by=By.CSS_SELECTOR, value='#container > div.contents > div.productWrapper > div.productMain > div.productMainTop > div > div.summaryBody > ul > li.infoItem.infoPrice > div > ul > li:nth-child(2) > div > div > li:nth-child(1) > strong')
                total_list = sale_list + price_list + price_etc_list + price_etc_list2
                if total_list:
                    a_price = total_list[0].text

            # 2차 크롤링 결과 print
            print('가격: ' + a_price + '/연령: ' + a_age_limit )

            # 장소 페이지로 이동
            driver.back()
            time.sleep(1)

            div = driver.find_element(by=By.CSS_SELECTOR, value= f'body > table > tbody > tr:nth-child(2) > td:nth-child(3) > div > div > div.con > div > table > tbody > tr:nth-child({i+1})')
            div.find_element(by=By.CSS_SELECTOR, value='td:nth-child(3) > a').click()
            time.sleep(0.3)


            # 장소 페이지에서 정보 크롤링(3차)
            address_list = []
            phone_num_list = []
            homepage_list = []
            a_address = ''
            a_phone_num = ''
            a_homepage = ''

            address_list = driver.find_elements(by=By.CSS_SELECTOR,
                                                value='body > table > tbody > tr:nth-child(2) > td:nth-child(3) > table > tbody > tr:nth-child(2) > td > table > tbody > tr > td:nth-child(2) > table > tbody > tr:nth-child(3) > td')
            phone_num_list = driver.find_elements(by=By.CSS_SELECTOR,
                                                  value='body > table > tbody > tr:nth-child(2) > td:nth-child(3) > table > tbody > tr:nth-child(2) > td > table > tbody > tr > td:nth-child(2) > table > tbody > tr:nth-child(4) > td')
            homepage_list = driver.find_elements(by=By.CSS_SELECTOR,
                                                 value='body > table > tbody > tr:nth-child(2) > td:nth-child(3) > table > tbody > tr:nth-child(2) > td > table > tbody > tr > td:nth-child(2) > table > tbody > tr:nth-child(5) > td')
            place_info = {}

            if address_list:
                a_address = address_list[0].text.strip('주     소 :')
            if a_place == '온라인':
                a_address = '온라인'
            if phone_num_list:
                a_phone_num = phone_num_list[0].text.strip('전     화 :')
            if homepage_list:
                a_homepage = homepage_list[0].text.strip('홈페이지 :')

            # 3차 크롤링 결과 프린트
            print('장소정보: ' + a_address + '/' + a_phone_num + '/' + a_homepage)
            print('-----------------------------------------------------------------------------')

            # 초기 페이지로 복귀
            driver.back()
            time.sleep(1)

            # 전시회 정보 mongoDB에 저장
            doc = {
                'title': a_title,
                'ticket_link': a_ticket_link,
                'image_link': a_image_link,
                'place': a_place,
                'place_link': a_place_link,
                'start_date': a_start_date,
                'end_date': a_end_date,
                'class': a_class,
                'price': a_price,
                'age_limit': a_age_limit,
                'address': a_address,
                'phone_num': a_phone_num,
                'place_homepage': a_homepage
            }
            db.exhibition_info.insert_one(doc)

        else:
            found_data = {}
            found_data = db.exhibition_info.find_one({'title':a_title})
            class_data_before = []
            class_data_before = found_data['class']
            class_data_after = class_data_before + [ class_url['class'] ]

            db.exhibition_info.update_one({'title': a_title}, {'$set': {'class': class_data_after}})

            print_class_str = ''
            for data_class in class_data_after:
                if str == '':
                    print_class_str = print_class_str + data_class
                else:
                    print_class_str = print_class_str + ', ' + data_class
            print(a_title + '// class 추가: ' + print_class_str)
            print('--------------------------------------------------------------------------------')

driver.close()
print('문제없이 완료!')