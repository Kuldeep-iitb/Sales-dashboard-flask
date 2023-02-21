from flask import Flask, render_template
import apikey as apikey
import requests
import json
from datetime import datetime, timedelta, date, time

from collections import Counter

# Feel free to import additional libraries if you like

app = Flask(__name__, static_url_path='/static')

# Paste the API-key you have received as the value for "x-api-key"


#get current date minus one year
def one_year():
    #today should equal current date but not time
    today = datetime.today()
    year = timedelta(days=365)
    return today - year

def one_month():
    today = datetime.today()
    month = timedelta(days=30)
    return today - month

print(one_year())
headers = {
        "Content-Type": "application/json",
        "Accept": "application/hal+json",
        "x-api-key": apikey.apikey
}


# Example of function for REST API call to get data from Lime
def get_api_data(headers, url):
    # First call to get first data page from the API
    response = requests.get(url=url,
                            headers=headers,
                            data=None,
                            verify=False)

    # Convert response string into json data and get embedded limeobjects
    json_data = json.loads(response.text)
    limeobjects = json_data.get("_embedded").get("limeobjects")

    # Check for more data pages and get thoose too
    nextpage = json_data.get("_links").get("next")
    while nextpage is not None:
        url = nextpage["href"]
        response = requests.get(url=url,
                                headers=headers,
                                data=None,
                                verify=False)

        json_data = json.loads(response.text)
        limeobjects += json_data.get("_embedded").get("limeobjects")
        nextpage = json_data.get("_links").get("next")

    return limeobjects
# Index page
@app.route('/')
def dashboard():
    
    # Example of API call to get deals
    base_url = "https://api-test.lime-crm.com/api-test/api/v1/limeobject/deal/"
    params = f"?_limit=50&_sort=-closeddate&dealstatus=agreement&min-closeddate={one_year()}"
    url = base_url + params
    #count deals

    response_deals = get_api_data(headers, url)
    #count deals
    print(len(response_deals))
    print(one_year())
    
    months = [datetime.today().replace(day=1) - timedelta(days=30*i) for i in range(12)]
    deals_month = Counter({m.strftime('%Y-%m'): 0 for m in months})
   
    deal_value = 0
    deals_year = 0
    
    # deals_month = []
    for deal in response_deals:
        deals_year += 1
        deal_value += deal.get("value")
        date = deal.get("closeddate").split("-")
        date = date[0] + "-" + date[1]
        if date in deals_month:
            deals_month[date] += 1
    deals_month = Counter(deals_month)

   

    #convert to json
    deals_month = json.dumps(deals_month)
    print(deals_month)
    deal_value = int(deal_value / len(response_deals))
    




    return render_template('dashboard.html', deal_value=deal_value, deals_month=deals_month, deals_year=deals_year)
    

# Example page
@app.route('/example')
def example():

    # Example of API call to get deals
    base_url = "https://api-test.lime-crm.com/api-test/api/v1/limeobject/deal/"
    params = f"?_limit=50&_sort=-closeddate&dealstatus=agreement&min-closeddate={one_year()}"
    url = base_url + params
    

    response_deals = get_api_data(headers, url)
    
    print(len(response_deals))

 
    months = [datetime.today().replace(day=1) - timedelta(days=30*i) for i in range(12)]
    deals_month = Counter({m.strftime('%Y-%m'): 0 for m in months})
    
    for deal in response_deals:
        date = deal.get("closeddate").split("-")
        date = date[0] + "-" + date[1]
        print(date)
        if date in deals_month:
            deals_month[date] += 1
        
    print(deals_month)
    print(months)

    
    deals_month = json.dumps(deals_month)
    deal_value = response_deals
    

    return render_template('example.html', deal_value=deal_value, deals_month=deals_month)


# You can add more pages to your app, like this:
@app.route('/customers')
#note to future self; take a look at Pagination (Target?), status is not correct
def customers():
    
    # Example of API call to get deals
    base_url = "https://api-test.lime-crm.com/api-test/api/v1/limetype/company/"
    params = "?_limit=5"
    url = base_url + params
    #count deals

    response = get_api_data(headers, url)
    #count deals
    companies = []
    for company in response:
        name = company["name"]
        buyingstatus = company["buyingstatus"]["text"]
        country = company["country"]
        city = company["visitingcity"]
        phone = company["phone"]
        companies.append({"name": name, "buyingstatus": buyingstatus, "country": country, "city": city, "phone": phone})
    print(companies)

    return render_template('customers.html', companies=companies)


# DEBUGGING
"""
If you want to debug your app, one of the ways you can do that is to use:
import pdb; pdb.set_trace()
Add that line of code anywhere, and it will act as a breakpoint and halt
your application
"""

if __name__ == '__main__':
    app.secret_key = 'somethingsecret'
    app.run(debug=True)
