from __future__ import print_function
import gevent
from gevent import monkey
import copy
# patches stdlib (including socket and ssl modules) to cooperate with other greenlets
monkey.patch_all()

import requests
from bs4 import BeautifulSoup
import urllib.request
from scrapy.selector import Selector

# Note that we're using HTTPS, so
# this demonstrates that SSL works

result_list = []

def return_page_response(url, query, temp=[]):
    response = Selector(text=urllib.request.urlopen(url).read())
    # print(len(temp))
    temp = temp + ['https://www.cars.com' + i.extract() for i in response.xpath(query)]
    if len(temp) < 50:
        next_page = response.xpath("//div[contains(@class, 'sds-pagination__controls')]/a[contains(@class, 'sds-button sds-button--secondary sds-pagination__control')]/@href")
        if next_page:
            temp = temp + return_page_response(url='https://www.cars.com' + next_page[0].extract(),query=query, temp=temp)
    return temp[:50]

def read_page(url):
    global result_list
    print("reading {}".format(url))
    query = "//div[contains(@class, 'vehicle-card   ')]/a[contains(@class, 'vehicle-card-visited-tracking-link')]/@href"
    res = return_page_response(url, query=query)
    print(len(res))
    jobs_car = [gevent.spawn(read_car, _url_car) for _url_car in res]

    gevent.wait(jobs_car)
    return_data = copy.deepcopy(result_list)
    result_list = []
    return return_data

def read_car(url):
    print(" ")
    print("=======================================")
    print(url)
    print("=======================================")
    print(" ")
    data = urllib.request.urlopen(url)
    response = Selector(text=data.read())
    image_url = check_none(response.xpath("//div[contains(@class, 'image-swipe-card')]/img[contains(@class, 'swipe-main-image image-index-0')]/@src"))
    car_price = check_none(response.xpath("//div[contains(@class, 'price-section  ')]/span[contains(@class, 'primary-price')]/text()"))
    car_year = check_none(response.xpath("//div[contains(@class, 'title-section')]/h1[contains(@class, 'listing-title')]/text()")).split(" ")[0]
    car_brand = check_none(response.xpath("//div[contains(@class, 'title-section')]/h1[contains(@class, 'listing-title')]/text()")).split(" ")[1:]
    advert_title = check_none(response.xpath("//div[contains(@class, 'title-section')]/h1[contains(@class, 'listing-title')]/text()"))
    info = [i.extract() for i in response.xpath("//dl[contains(@class, 'fancy-description-list')]//dd/text()")]
    exterior_color = info[0]
    transmission = info[6]
    item= {}
    item["image_url"]= image_url
    item["car_price"]= car_price
    item["car_year"]= car_year
    item["car_brand"]= " ".join(car_brand)
    item["advert_title"] = advert_title
    item["exterior_color"] = exterior_color
    item["transmission"] = transmission
    result_list.append(item)

def check_none(x_path):
    return x_path[0].extract() if len(x_path)>0 else None

def start_read(url):
    data = requests.get(url)
    soup=BeautifulSoup(data.content,'lxml')
    car_url_list = soup.select('div.vehicle-card-visited-tracking-link a')

