import car_search
import crochet
crochet.setup()
import os
from flask import Flask , render_template, jsonify, request, redirect, url_for
from scrapy.crawler import CrawlerRunner
import json
import copy

app = Flask(__name__)

output_data = []
crawl_runner = CrawlerRunner()


@app.route('/')
def index():
    color_list = [{'name':'Beige', 'value':'beige'}, {'name':'Black', 'value':'black'}, {'name':'Blue', 'value':'blue'}, {'name':'Brown','value':'brown'}, {'name':'Gold', 'value':'gold'}, {'name':'Gray', 'value':'gray'}, {'name':'Green','value':'green'}, {'name':'Orange', 'value':'orange'}, {'name':'Purple', 'value':'purple'}, {'name':'Red', 'value':'red'}, {'name':'Silver', 'value':'silver'}, {'name':'White', 'value':'white'}, {'name':'Yellow', 'value':'yellow'}]
    transmission_list = [{'name':'Automanual', 'value':'automanual'}, {'name':'Automatic', 'value':'automatic'}, {'name':'CVT','value':'cvt'}, {'name':'Manual', 'value':'manual'}, {'name':'Unknown','value':'unknown'}]
    x = list(map(str, range(1950,2023)))
    date = [{'name':str(i)} for i in x]
    return render_template("index.html", date=date,
    color=color_list, transmission=transmission_list)


@app.route('/', methods=['POST'])
def submit():
    if request.method == 'POST':
        search_url = []
        search_url.append("keyword=" + request.form['brand']) if request.form['brand'] else ""
        search_url.append("exterior_color_slugs[]=" + request.form['ext_color'])  if request.form['ext_color'] else ""
        search_url.append("year_min=" + request.form['min_year']) if request.form['min_year']  else ""
        search_url.append("year_max=" + request.form['max_year']) if request.form['max_year']  else ""
        search_url.append("transmission_slugs[]=" + request.form['transmission']) if request.form['transmission'] else "" 

        global baseURL
        baseURL = 'https://www.cars.com/shopping/results/'
        'https://www.cars.com/shopping/results/?exterior_color_slugs[]=black'
        
        if os.path.exists("<data.json.json>"): 
        	os.remove("<data.json.json>")

        url = "list"
        if len(search_url) > 0:
            url = "list?" + "&".join(search_url)

        return redirect(url_for('scrape',url=url)) 

def result(data):
    data_json = copy.deepcopy(data)
    json_count = len(data_json)
    print(len(data_json))
    return render_template("result.html", json_count= json_count, json_data=json.dumps(data_json, default=set_default))#,

@app.route("/cars/<string:url>")
async def scrape(url):
    start_url = 'https://www.cars.com/shopping/results/'
    if len(url.split('list')) > 0:
        start_url = start_url + url.split('list')[1]
    result_data = car_search.read_page(start_url)
    output_json = {i: result_data[i] for i in range(len(result_data))}
    with open('data.json', 'w') as f:
        json.dump(output_json, f)
    print("===================================")
    print(len(result_data))
    res = result(output_json)
    del result_data
    del output_json

    return res

def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError

if __name__== "__main__":
    app.run(debug=True)