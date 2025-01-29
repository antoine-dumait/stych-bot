import scrapper
import time

while True:
    scrapper.fetch_courses()
    time.sleep(5*60) # Wait 5 min