import time
import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import pandas as pd
import re
from webdriver_manager.chrome import ChromeDriverManager
service = Service(executable_path=ChromeDriverManager().install()) #automatifally downloads chrome webdriver and saves it in cache
driver = webdriver.Chrome(service=service)
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service)


#path for the new english metadata
en_metadata_path = '/Users/tojo/Desktop/text_analysis_vanderbilt/gutenberg/metadata/en_metadata.csv'
def read_file(path): #to read csv files with pandas
    df = pd.read_csv(path)
    return df

def get_publish_year(): #a function to crawl the book pages
    df = read_file(en_metadata_path)
    titles = list(df['title'])
    authors = list(df['author'])
    driver.get('https://www.worldcat.org/')
    time.sleep(3) #gives the page some time to load
    driver.find_element(by=By.ID, value='onetrust-accept-btn-handler').click() #accept cookies
    for i in range(len(titles)): # a loop to search the books by title
        search_box = driver.find_element(by=By.ID, value='q1') #accessing search box
        search_box.send_keys(str(titles[i]) + ' by ' + str(authors[i])) #feeding strings to the text box (title by author gives the most accurate result)
        search_box.send_keys(Keys.ENTER) #enter search by emulating the ENTER keyboard
        time.sleep(3) # give time for the result page to load
        title_match = False # a boolean to check if the result matches our input search
        results = driver.find_elements(by=By.CSS_SELECTOR, value='td.result.details') # getting each book from the search result
        for items in results:
            try:
                # this method makes sure that the items are only when the page loads, with 5 seconds max of wait time
                title = WebDriverWait(items, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR,'strong'))).text.split()
                for aut in title:
                    if aut.lower() in titles[i].lower():
                        title_match = True # if the title of the result matches the title from our metadata, we change the value of title_match to True
                    else:
                        title_match = False                   
            except selenium.common.exceptions.TimeoutException: # if nothing loads after 5 seconds, that means there is no content, so we skip
                pass
            if title_match == True:
                # there are two ways a book is displayed in the search result: a single book or a list of editions
                try:
                    # If there are multiple editions, this section will go through through the list and get the pub date of the oldest one
                    items.find_element(by=By.XPATH, value='//*[@id="br-table-results"]/tbody/tr[1]/td[4]/ul/li/a').click()
                    edition = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="resultsform"]/table/tbody/tr'))) 
                    print(len(edition)) 
                    first_ed = edition[-1]
                    iterable = len(edition)
                    while len(edition) > 0:
                        try:
                            rel_year = first_ed.find_element(by=By.XPATH, value='//*[@id="resultsform"]/table/tbody/tr[{}]/td[7]/div'.format(str(iterable))).text
                            print(rel_year)
                            break
                        except selenium.common.exceptions.NoSuchElementException:
                            iterable -= 1
                    break
                except selenium.common.exceptions.NoSuchElementException:
                    # If only a single edition is available, this section will get the pub year of that book
                    items.find_element(by=By.CSS_SELECTOR, value='a').click()
                    time.sleep(3)
                    driver.refresh()
                    time.sleep(3)
                    publication = driver.find_element(by=By.XPATH, value='//*[@id="bib-publisher-cell"]').text
                    publication = re.sub('\D', '', publication)
                    rel_year = int(publication)
                    print('no multiple edition available')
                    print(rel_year)
                    break
        driver.find_element(by=By.ID, value='home-links').click()
        time.sleep(3)
get_publish_year()