from collections import Counter
from flask import Flask, render_template, url_for, request
import apikey as apikey
import requests
import json
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, static_url_path='/static')



headers = {
    "Content-Type": "application/json",
    "Accept": "application/hal+json",
    "x-api-key": apikey.apikey
}

def get_api_data(headers, url):
    
    response = requests.get(url=url,
                            headers=headers,
                            data=None,
                            verify=False)


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

def get_api_data_next(headers, url):
    response = requests.get(url=url,
                            headers=headers,
                            data=None,
                            verify=False)

    # Convert response string into json data and get embedded limeobjects
    json_data = json.loads(response.text)
    limeobjects = json_data.get("_embedded").get("limeobjects")
    
    nextpage = json_data.get("_links").get("next")
    for item in limeobjects:
        item['next'] = nextpage
    return limeobjects

# get current date minus one year
def one_year():
    today = datetime.today()
    year = timedelta(days=365)
    return today - year



@app.route('/')
def dashboard():

    base_url = "https://api-test.lime-crm.com/api-test/api/v1/limeobject/deal/"
    params = f"?_limit=50&_sort=-closeddate&dealstatus=agreement&min-closeddate={one_year()}&_embed=company"
    url = base_url + params

    deals = get_api_data(headers, url)
    
    companies = [deal["_embedded"]["relation_company"] for deal in deals]
    
    # Initialize variables
    company_totals = {}
    companies_with_deals = {}
    deal_value = 0
    deals_year = 0

    #returns array of ex. (2023, 2, 27, 9, 20, 10, 461091)
    months = [datetime.today() - timedelta(days=30*i) for i in range(13)] 
    #converts months to strings and assign value 0 ex. "2023-02': 0"
    deals_month = Counter({m.strftime('%Y-%m'): 0 for m in months}) 
    

    
    for deal in deals:
        # extract the company ID and deal value
        deal_id = deal['company']
        value = deal['value']
        # update total deals/year and deal value/year
        deals_year += 1
        deal_value += deal['value']
        # get date in correct format
        date = deal['closeddate'].split("-")
        date = date[0] + "-" + date[1]
        # increment ammount of deals at current month
        if date in deals_month:
            deals_month[date] += 1
        # update total value for each company
        if deal_id in company_totals:
            company_totals[deal_id] += value
        else:
            company_totals[deal_id] = value
    
    
    deals_month = json.dumps(deals_month)
    deal_value_year = int(deal_value)
    deal_value = int(deal_value / len(deals))
    customers_year = len(company_totals)

    # update the companies_with_deals dictionary with the total value of deals for each company
    for company in companies:
        company_id = company['_id']
        if company_id in company_totals:
            name = company.get('name')
            total_value = company_totals[company_id]
            companies_with_deals[name] = total_value

    companies_with_deals = json.dumps(companies_with_deals)
    print(companies_with_deals)
    print(company_totals)

    return render_template('dashboard.html', deal_value=deal_value, deal_value_year=deal_value_year, deals_month=deals_month, deals_year=deals_year, customers_year=customers_year, companyTotalYear=companies_with_deals)


@app.route('/customers')
def customers():
    limit = 35 # set limit of data to get from API
    offset = request.args.get('offset', default=0, type=int)
    base_url = "https://api-test.lime-crm.com/api-test/api/v1/limeobject/company/"
    params = f"?_limit={limit}&_sort=-_timestamp&_offset={offset}"
    url = base_url + params

    company_res = get_api_data_next(headers, url)

    base_url = "https://api-test.lime-crm.com/api-test/api/v1/limeobject/deal/"
    params = f"?_limit={limit}&_sort=-closeddate&dealstatus=agreement&_offset={offset}"
    url = base_url + params

    deals_res = get_api_data_next(headers, url)
   
    next_offset = offset + limit if len(company_res) == limit else None
    prev_offset = offset - limit if offset > 0 else None
   
    
    deals_filtered = [{"company": deal["company"],"value": deal["value"] , "closeddate": deal["closeddate"] } for deal in deals_res]
    deals_last_year = [deal for deal in deals_filtered if deal["closeddate"] > one_year().strftime("%Y-%m-%d")]

    companies_filtered = [{"name": company["name"], "company_id": company["_id"],
                  "country": company["country"], "city": company["visitingcity"], "phone": company["phone"], "status": company["buyingstatus"]["key"]} for company in company_res]
    customers = []
    prospects = []
    inactive = []
    
    # Iterate over the companies and assign a status to each one based on whether it has had any deals in the last year
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

    # Sort the customers by by deal value
    customers.sort(key=lambda x: x["value"], reverse=True)
    
    companies = customers + prospects + inactive
  

    return render_template('customers.html', companies=companies, next_offset=next_offset, prev_offset=prev_offset)


if __name__ == '__main__':
    app.secret_key = 'somethingsecret'
    app.run(debug=True)
