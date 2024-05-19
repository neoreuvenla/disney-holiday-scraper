# config.py

# switch to shorter ranges for faster function checking
debug = True

# booking urls
disney_home = 'https://www.disneyholidays.co.uk/walt-disney-world/'

# set an upper limit to random sleep second generation
pagination_sleep = 1
search_sleep = 2

# static search data that remains the same for each enquiry
adults = 2
children = 0

# ranged search data that changes for each enquiry
if debug == True:  # smaller date range for quick test function
    airports = ['LON', 'MAN']
    days = list(map(str, range(10, 14)))
    months = [f'{month}^{year}' for month in range(1, 2) for year in [2025]]
    nights = list(map(str, range(12, 15)))
else:  # full date range for full data scraping
    airports = ['LON', 'MAN']  # note that most regional airports can only be booked 11 months ahead
    days = list(map(str, range(1, 31)))

    # decide between non-school holiday months or full 12 months
    months = [f'{month}^{year}' for month in [1, 2, 3, 4, 5, 6, 9, 10, 11, 12] for year in [2025]]
    #months = [f'{month}^{year}' for month in range(1, 13) for year in [2025]]  # for full 12 months

    nights = list(map(str, range(7, 13)))
