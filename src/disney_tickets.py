# disney_tickets.py
 
import concurrent.futures
from bs4 import BeautifulSoup
import pandas as pd
import random
import requests
import time
from tqdm import tqdm
# import settings from config file
from config import disney_home, search_sleep, pagination_sleep, days, months, nights, adults, children

# construct static search data from config
static_data = {
    'holiday': 'Tickets',
    'adults': adults,
    'children': children}

# extracts ticket information from a result page
def extract_tickets(page_url, session, nights):
    ticket_details = []

    # access the webpage and find all hotel divs
    response = session.get(page_url, timeout=20)
    soup = BeautifulSoup(response.content, 'html.parser')

    # ticket page will default to 14 day ticket if over 14 nights are selected
    if nights < 14:
        tickets = soup.find('div', class_='type seven small-12 medium-12')
    else:
        tickets = soup.find('div', class_='type fourteen small-12 medium-12')

    prices = soup.find('div', class_='price horizontal')

    # attempt to retrieve ticket name
    try:
        name = tickets.find('div', class_='heading').h2.get_text(strip=True)
    except AttributeError:
        name = 'N/A'
    
    # attempt to retrieve price
    try:
        price_pounds = prices.find('span').get_text(strip=True)
    except AttributeError:
        price_pounds = 'N/A'

    # attempt to find deals
    try:
        deal_text = tickets.find('li', class_='icon promo').find('strong').get_text(strip=True)
    except AttributeError:
        deal_text = 'N/A'

    # add retrieved values to list
    ticket_details.append({
        'Ticket': name,
        'Price (GBP)': price_pounds,
        'Deal': deal_text})
    
    return ticket_details

# submits search queries to webpage
def submit_search(form_data, session):

    # retry attempts to handle unsuccessful attempts
    for attempt in range(3):

        # attempt to submit search and navigate response pages for data extraction
        try:
            response = session.post(disney_home, data=form_data, timeout=20)
            response.raise_for_status()

            return extract_tickets(response.url, session, int(form_data['nights']))
        
        # random sleep before retrying with exponential backoff
        except requests.RequestException as e:

            time.sleep(random.uniform(1, search_sleep ** attempt))
    
    return []

# spawns workers for multithreading speed up
def worker(day, month, night):
    
    # simulate making a request to the server to avoid detection
    time.sleep(random.uniform(0.5, search_sleep))
    session = requests.Session()
    
    # copy the static data and modify with specific search details
    search_data = static_data.copy()
    search_data.update({
        'day': day,       
        'month': month,     
        'nights': night})
    
    # search and update found data with the search parameters used
    ticket_details = submit_search(search_data, session)
    for info in ticket_details:
        info.update(search_data)
    
    return ticket_details

# start processing timer and print start message
start_time = time.time()
print("\n$$$ Ticket Prices Scraping Started $$$")

# create threads to loop through all search parameter combinations
all_results = []
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    
    # add each combination to the list for execution
    futures = [] 
    for day in days:
        for month in months:
            for night in nights:
                futures.append(executor.submit(worker, day, month, night))

    # track completion of tasks and adding to list using a progress bar
    with tqdm(total=len(futures)) as pbar:
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            all_results.extend(result)
            pbar.update(1)

# export results to csv
export_data = pd.DataFrame(all_results)
export_data.to_csv('output/disney_tickets.csv', index=False)

# print the output block
end_time = time.time()
total_time = end_time - start_time
print(f"!!! Ticket Prices Scraping Completed !!!")
print(f"   @@@ {len(all_results)} entries")
print(f"   @@@ Executed In: {total_time:.2f} seconds\n")