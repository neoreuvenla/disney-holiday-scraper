# disney_hotels.py
 
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
    'holiday': 'Hotel',
    'adults': '2',
    'children': '0',
    'hotel-category': 'ALL'}

# extracts hotel information from a result page
def extract_hotels(page_url, session):
    hotel_details = []

    # access the webpage and find all hotel divs
    response = session.get(page_url, timeout=20)
    soup = BeautifulSoup(response.content, 'html.parser')
    hotels = soup.find_all('div', class_='accommodation')

    # loop through all the hotels on the page
    for hotel in hotels:
                
        # attempt to extract airline name from div
        try:
            name = hotel.find('div', class_='info').h2.get_text(strip=True)
        except AttributeError:
            name = 'N/A'

        # attempt to extract the price
        try:
            price_pounds = hotel.find('span', class_='pounds').get_text(strip=True)
        except AttributeError:
            price_pounds = 'N/A'

        # attempt to find deals
        try:
            deal_text = hotel.find('div', class_='deal').h4.get_text(strip=True)
        except AttributeError:
            deal_text = 'N/A'
        
        # add hotel information to the list
        hotel_details.append({
            'Hotel': name,
            'Price (GBP)': price_pounds,
            'Deal': deal_text})
    
    return hotel_details

# navigates through multi page response content
def page_navigation(starting_url, session):
    pages = []
    all_hotels = [] 

    # access the webpage and find all hotel divs
    response = session.get(starting_url, timeout=20)
    soup = BeautifulSoup(response.content, 'html.parser')
    pagination_links = soup.select('div.links a.page')

    # loop through all the result pages
    for link in pagination_links:

        # construct full url for each link and add to list
        if 'href' in link.attrs:
            page_url = link['href']
            pages.append(f"{disney_home}{page_url}")
    
    # insert the starting page as the first page in the list
    pages.insert(0, starting_url)

    # extract hotels from the page and sleep to avoid bot detection
    for page in pages:
        all_hotels.extend(extract_hotels(page, session))
        time.sleep(random.uniform(0.5, pagination_sleep))
    
    return all_hotels

# submits search queries to webpage
def submit_search(form_data, session):

    # retry attempts to handle unsuccessful attempts
    for attempt in range(3):

        # attempt to submit search and navigate response pages for data extraction
        try:
            response = session.post(disney_home, data=form_data, timeout=20)
            response.raise_for_status()
            return page_navigation(response.url, session)
        
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
    hotel_details = submit_search(search_data, session)
    for info in hotel_details:
        info.update(search_data)
    
    return hotel_details

# start processing timer and print start message
start_time = time.time()
print("\n$$$ Hotel Prices Scraping Started $$$")

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
export_data.to_csv('output/disney_hotels.csv', index=False)

# print the output block
end_time = time.time()
total_time = end_time - start_time
print(f"!!! Hotel Prices Scraping Completed !!!")
print(f"   @@@ {len(all_results)} entries")
print(f"   @@@ Executed In: {total_time:.2f} seconds\n")