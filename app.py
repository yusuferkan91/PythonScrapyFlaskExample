import car_search
import os
from flask import Flask , render_template, request, redirect, url_for
import json

app = Flask(__name__)

@app.route('/')
def index():
    url = "https://www.cars.com/shopping/results/?page_size=50&"
    color_list, transmission_list = car_search.get_search_options(url)
    date = [{'name':str(i)} for i in range(1970, 2024)]

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
        
        if os.path.exists("<data.json.json>"): 
        	os.remove("<data.json.json>")
        
        url = "list" + "&".join(search_url) if len(search_url) > 0 else "list"

        return redirect(url_for('scrape',url=url)) 

@app.route("/cars/<string:url>")
def scrape(url):
    start_url = 'https://www.cars.com/shopping/results/?page_size=50&'

    if len(url.split('list')) > 0:
        start_url = start_url + url.split('list')[1]

    result_data = car_search.read_page(start_url)
    output_json = {i: result_data[i] for i in range(len(result_data))}

    with open('data.json', 'w') as f:
        json.dump(output_json, f)

    return render_template("result.html", json_count= len(output_json), json_data=json.dumps(output_json, default=set_default))

def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError

if __name__== "__main__":
    app.run(debug=True)