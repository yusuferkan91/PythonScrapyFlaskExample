from __future__ import print_function
import gevent
from gevent import monkey
import copy
monkey.patch_all()
import urllib.request
from scrapy.selector import Selector

result_list = []

def return_page_response(url, query):
    response = Selector(text=urllib.request.urlopen(url).read())

    return ['https://www.cars.com' + i.extract() for i in response.xpath(query)]

def read_page(url):
    global result_list
    
    query = "//div[contains(@class, 'vehicle-card   ')]/a[contains(@class, 'vehicle-card-visited-tracking-link')]/@href"
    res = return_page_response(url, query=query)
    
    print("reading {}".format(url))
    print(len(res))

    jobs_car = [gevent.spawn(read_car, _url_car) for _url_car in res]
    gevent.wait(jobs_car)

    return_data = copy.deepcopy(result_list)
    result_list = []

    return return_data

def read_car(url):
    response = Selector(text=urllib.request.urlopen(url).read())
    
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

def get_search_options(url):
    response = Selector(text=urllib.request.urlopen(url).read())

    query_color = "//div[contains(@id, 'panel_exterior_colors')]//div[contains(@class, 'sds-checkbox')]//div[contains(@class, 'color-swatch')]/following-sibling::text()"
    query_transmission = "//div[contains(@id, 'panel_transmissions')]//div[contains(@class, 'sds-checkbox')]//label[contains(@class, 'sds-label')]/text()"

    return parse_query(response, query=query_color), parse_query(response, query=query_transmission)

def parse_query(response, query):
    lst = []
    for i in response.xpath(query=query):
        item = i.extract().replace(" ", "").replace("\n", "")
        if item:
            lst.append({"name": item, "value": item.lower()})
            
    return lst