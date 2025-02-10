import scrapper
import time

while True:
    print(f'Stych courses Fetching in process...')
    scrapper.fetch_courses()
    print(f'Wait 5 min...')
    time.sleep(5*60) # Wait 5 min
