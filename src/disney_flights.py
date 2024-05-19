# disney_flights.py
 
import concurrent.futures
from bs4 import BeautifulSoup
import pandas as pd
import random
import requests
import time
from tqdm import tqdm
# import settings from config file
from config import disney_home, search_sleep, pagination_sleep, days, months, nights, adults, children, airports

# construct static search data from config
static_data = {
    'holiday': 'Flights',
    'adults': adults,
    'children': children,
    'flights-to': 'MCO',
    'flights-cabin': 'Economy'}

# extracts flight information from a result page
def extract_flights(page_url, session):
    flight_details = []

    # access the webpage and find all flight divs
    response = session.get(page_url, timeout=20)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # check for flight dive and reassign to flight last if missing
    flights = soup.find_all('div', class_='flight')
    if not flights:
        flights = soup.find_all('div', class_='flight last')
    
    # loop through all the flights on the page
    for flight in flights:
                
        # attempt to extract airline name from div
        try:
            airline = flight.find('div', class_='airline').h2.get_text(strip=True)
        except AttributeError:
            airline = 'N/A'
        
        # extract direct flight info and skip indirect flights
        indirect = flight.find('small', class_='indirect')
        direct = flight.find('small', class_='direct')
        if indirect:
            continue
        else:
            flight_type = direct.get_text(strip=True)
        
        # attempt to extract the price
        try:
            price_pounds = flight.find('span', class_='pounds').get_text(strip=True)
        except AttributeError:
            price_pounds = 'N/A'

        # attempt to find deals
        try:
            deal_text = flight.find('div', class_='deal').h4.get_text(strip=True)
        except AttributeError:
            deal_text = 'N/A'
        
        # add flight information to the list
        flight_details.append({
            'Airline': airline,
            'Type': flight_type,
            'Price (GBP)': price_pounds,
            'Deal': deal_text})

    return flight_details

# navigates through multi page response content
def page_navigation(starting_url, session):
    pages = []
    all_flights = [] 

    # access the webpage and find all flight divs
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

    # extract flights from the page and sleep to avoid bot detection
    for page in pages:
        all_flights.extend(extract_flights(page, session))
        time.sleep(random.uniform(0.5, pagination_sleep))
    
    return all_flights

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
def worker(airport, day, month, night):
    
    # simulate making a request to the server to avoid detection
    time.sleep(random.uniform(0.5, search_sleep))
    session = requests.Session()
    
    # copy the static data and modify with specific search details
    search_data = static_data.copy()
    search_data.update({
        'day': day,       
        'month': month,     
        'nights': night,    
        'flights-from': airport})
    
    # search and update found data with the search parameters used
    flight_details = submit_search(search_data, session)
    for info in flight_details:
        info.update(search_data)
    
    return flight_details

# start processing timer and print start message
start_time = time.time()
print("\n$$$ Flight Prices Scraping Started $$$")

# create threads to loop through all search parameter combinations
all_results = []
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    
    # add each combination to the list for execution
    futures = [] 
    for airport in airports:
        for day in days:
            for month in months:
                for night in nights:
                    futures.append(executor.submit(worker, airport, day, month, night))

    # track completion of tasks and adding to list using a progress bar
    with tqdm(total=len(futures)) as pbar:
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            all_results.extend(result)
            pbar.update(1)

# export results to csv
export_data = pd.DataFrame(all_results)
export_data.to_csv('output/disney_flights.csv', index=False)

# print the output block
end_time = time.time()
total_time = end_time - start_time
print(f"!!! Flight Prices Scraping Completed !!!")
print(f"   @@@ {len(all_results)} entries")
print(f"   @@@ Executed In: {total_time:.2f} seconds\n")