from collections import Counter
from flask import Flask, render_template
import apikey as apikey
import requests
import json
from datetime import datetime, timedelta, date, time
import logging

logging.basicConfig(level=logging.DEBUG)


# Feel free to import additional libraries if you like

app = Flask(__name__, static_url_path='/static')

# Paste the API-key you have received as the value for "x-api-key"


# get current date minus one year
def one_year():
    # today should equal current date but not time
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
    base_url = "https://api-test.lime-crm.com/api-test/api/v1/limeobject/company/"
    params = "?_limit=50"
    url = base_url + params
    # Example of API call to get deals
    companies = get_api_data(headers, url)

    # Example of API call to get deals

    ## KOLLA EMDED COMPANY
    ## KOLLA EMDED COMPANY
    ## KOLLA EMDED COMPANY
    base_url = "https://api-test.lime-crm.com/api-test/api/v1/limeobject/deal/"
    params = f"?_limit=50&_sort=-closeddate&dealstatus=agreement&min-closeddate={one_year()}"
    url = base_url + params

    deals = get_api_data(headers, url)

    company_totals = {}
    companies_with_deals = {}

    months = [datetime.today() - timedelta(days=30*i) for i in range(13)]
    deals_month = Counter({m.strftime('%Y-%m'): 0 for m in months})

    deal_value = 0
    deals_year = 0

    # deals_month = []
    for deal in deals:
        deal_id = deal['company']
        value = deal['value']
        deals_year += 1
        deal_value += deal.get("value")
        date = deal.get("closeddate").split("-")
        date = date[0] + "-" + date[1]
        if date in deals_month:
            deals_month[date] += 1
        if deal_id in company_totals:
            company_totals[deal_id] += value
        else:
            company_totals[deal_id] = value

    deals_month = Counter(deals_month)
    deals_month = json.dumps(deals_month)
    deal_value_year = int(deal_value)
    deal_value = int(deal_value / len(deals))
    customers_year = len(company_totals)

    # for company in companies:
    #     company_id = company['_id']
    #     if company_id in company_totals:
    #         company['total_value'] = company_totals[company_id]
    #         companies_with_deals.append({'name': company.get(
    #             'name'), 'total': company.get('total_value')})

    for company in companies:
        company_id = company['_id']
        if company_id in company_totals:
            name = company.get('name')
            total_value = company_totals[company_id]
            companies_with_deals[name] = total_value

    companies_with_deals = json.dumps(companies_with_deals)

    return render_template('dashboard.html', deal_value=deal_value, deal_value_year=deal_value_year, deals_month=deals_month, deals_year=deals_year, customers_year=customers_year, companyTotalYear=companies_with_deals)


# Example page
@app.route('/example')
def example():

    base_url = "https://api-test.lime-crm.com/api-test/api/v1/limeobject/company/"
    params = "?_limit=50"
    url = base_url + params
    # Example of API call to get deals
    companies = get_api_data(headers, url)

   
    # else:
    #     company['total_value'] = 0

    
    return render_template('example.html', companies=companies)


# You can add more pages to your app, like this:
@app.route('/customers')
# note to future self; take a look at Pagination (Target?), status is not correct
def customers():

    base_url = "https://api-test.lime-crm.com/api-test/api/v1/limeobject/company/"
    params = "?_limit=50"
    url = base_url + params
    company_res = get_api_data(headers, url)

    base_url = "https://api-test.lime-crm.com/api-test/api/v1/limeobject/deal/"
    params = "?_limit=50&_sort=-closeddate&dealstatus=agreement"
    url = base_url + params

    
    deals_res = get_api_data(headers, url)
    #get 'company' from deals_res and compare to 'company_id' in company_res where closeddate is within the last year
    deals_filtered = [{"company": deal["company"],"value": deal["value"] , "closeddate": deal["closeddate"] } for deal in deals_res]
    deals_last_year = [deal for deal in deals_filtered if deal["closeddate"] > one_year().strftime("%Y-%m-%d")]

    companies_filtered = [{"name": company["name"], "company_id": company["_id"],
                  "country": company["country"], "city": company["visitingcity"], "phone": company["phone"], "status": company["buyingstatus"]["key"]} for company in company_res]
    customers = []
    prospects = []
    inactive = []
    #sort customers by value
    

    #check if company_id is in deals_last_year
    for company in companies_filtered:
        if company["company_id"] in [deal["company"] for deal in deals_last_year]:
            company["status"] = "customer"
            company["value"] = int(sum([deal["value"] for deal in deals_last_year if deal["company"] == company["company_id"]]))
            customers.append(company)

        elif company["company_id"] not in [deal["company"] for deal in deals_filtered]:
            if company["status"] == "notinterested":
                company["status"] = "not interested"
            else: company["status"] = "prospect"
            prospects.append(company)

        else:
            company["status"] = "inactive"
            inactive.append(company)

    customers.sort(key=lambda x: x["value"], reverse=True)
    
    companies = customers + prospects + inactive   

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
