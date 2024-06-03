#National Rail Version
import nltk
from nltk import word_tokenize, pos_tag, ne_chunk
import numpy

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, \
    ElementClickInterceptedException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import time
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="urllib3")

user_agent = 'Chrome/88.0.4324.182 Safari/537.36'
chrome_options = Options()
chrome_options.add_argument(f'user-agent={user_agent}')

def click_cookie(driver):
    try:
        button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
        button.click()
        print('Clicked on cookie consent')
    except Exception as e:
        print('Error clicking on cookie consent:', e)

def extract_locations(text):
    tokens = word_tokenize(text)
    tagged = pos_tag(tokens)
    entities = ne_chunk(tagged)
    locations = []
    for entity in entities:
        if isinstance(entity, nltk.tree.Tree):
            if entity.label() == 'GPE':  # Geo-Political Entity, often locations
                locations.append(' '.join([child[0] for child in entity]))
    return locations

def click_journey(driver):
    try:
        plan_journey = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="jp-form-preview"]/section/div/button')))
        plan_journey.click()
    except TimeoutException:
        print("Timeout when clicking plan your journey")

def departure(driver, origin, destination):
    try:
        board = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="jp-form-preview"]/section/div/button')))
        board.click()
        print('Clicked on departure board')

        for attempt in range(3):
            try:
                origin_input = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'jp-origin')))
                origin_input.clear()
                origin_input.send_keys(origin)

                destination_input = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'jp-destination')))
                destination_input.clear()
                destination_input.send_keys(destination)

                print('Entered origin and destination:', origin, destination)
                break
            except StaleElementReferenceException:
                print(f"Stale element reference, retrying {attempt + 1}")

    except TimeoutException:
        print('Departure input not found')
    except Exception as e:
        print('Error occurred during departure input:', e)


def get_user_input():
    departure_location = input("Please enter your departure location: ")
    destination_location = input("Please enter your destination location: ")
    choose_date = input("Please enter your departure date: ")
    choose_hour = input("Please enter your departure time: ")
   # passenger_number = input("How many passengers are there?: ")
    return departure_location, destination_location, choose_date, choose_hour #passenger_number


def input_locations(driver, departure_location, destination_location):
    try:
        departure_input = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "jp-origin"))
        )
        departure_input.clear()
        departure_input.send_keys(departure_location)
        print("Departure location entered:", departure_location)

        destination_input = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "jp-destination"))
        )
        destination_input.clear()
        destination_input.send_keys(destination_location)
        print("Destination location entered:", destination_location)

    except Exception as e:
        print("Error occurred while inputting locations:", e)


def input_departure_date(driver, choose_date):
    try:
        date_input = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, 'leaving-date'))
        )
        date_input.click()
        time.sleep(3)

        # Use JavaScript to set the date directly if the datepicker is difficult to interact with
        driver.execute_script("arguments[0].value = '';", date_input)
        date_input.clear()
        date_input.clear()
        time.sleep(4)
        date_input.send_keys(choose_date)
        print("Date inserted:", choose_date)
    except TimeoutException:
        print("Timeout occurred while waiting for departure date input")
    except Exception as e:
        print("Error occurred while inputting departure date:", e)


def select_departure_hour(driver, hour):
    try:
        hour_dropdown = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="leaving-hour"]')))
        select = Select(hour_dropdown)
        select.select_by_visible_text(hour)
        print("Selected departure hour:", hour)
    except TimeoutException:
        print("Timeout occurred while waiting for departure hour dropdown")
    except Exception as e:
        print("Error occurred while selecting departure hour:", e)



"""
def input_passengers(driver, passenger_number):
    try:
        adults = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, 'adults')))
        adults.clear()
        time.sleep(3)
        adults.send_keys(passenger_number)
        print("Adult passengers entered:", passenger_number)
    except TimeoutException:
        print("Timeout occurred waiting for passenger input")
    except Exception as e:
        print("Error occurred while inputting passengers:", e)
"""


def click_show_trains(driver):
    global show_trains
    try:
        show_trains = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, 'button-jp')))
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element((By.CLASS_NAME, 'react-datepicker__day--0')))
        driver.execute_script("arguments[0].scrollIntoView();", show_trains)
        driver.execute_script("arguments[0].click();", show_trains)

        print('Clicked on show live trains')
    except TimeoutException:
        print('Timeout occurred while waiting for show live trains button')
    except ElementClickInterceptedException:
        print('Element click intercepted, retrying...')
        driver.execute_script("arguments[0].click();", show_trains)


def click_feedback(driver):
    try:
        click_no = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="fsrInvite"]/section[3]/button[2]')))
        time.sleep(2)
        click_no(driver)
        print("No feedback clicked")
    except TimeoutException:
        print("timeout occurred whilst waiting for feedback click")


def extract_train_ticket(driver):
    try:
        ticket_elements = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="outward-0"]/div/div/div[4]/div[1]/a'))
        )
        ticket_links = [elem.get_attribute('href') for elem in ticket_elements]
        return ticket_links
    except TimeoutException:
        print('timeout occurred whilst waiting for ticket links')
        return []


def main(destination, departure, date, hour, passengers):
    driver = webdriver.Chrome()
    driver.get("https://www.nationalrail.co.uk")
    click_cookie(driver)
    click_journey(driver)
    # Get user input for departure and destination locations
    # departure_location, destination_location,choose_date,choose_hour = get_user_input()

    departure_location, destination_location, choose_date, choose_hour = departure, destination, date, hour

    # Input locations on the webpage
    input_locations(driver, departure_location, destination_location)
    # Input departure time
    input_departure_date(driver, choose_date)
    time.sleep(3)
    select_departure_hour(driver, choose_hour)
    #input_passengers(driver, passenger_number)
    click_show_trains(driver)
    click_feedback(driver)
    ticket_links = extract_train_ticket(driver)
    if ticket_links:
        print("Train ticket link:")
        for link in ticket_links:
            print(link)
        return ticket_links
    else:
        print("Failed to retrieve ticket link")

    time.sleep(160)
    driver.quit()


if __name__ == "__main__":
    main()
