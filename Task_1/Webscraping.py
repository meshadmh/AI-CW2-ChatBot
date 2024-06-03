
import nltk
from nltk import word_tokenize, pos_tag, ne_chunk


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
    #
    try:
        plan_journey = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="jp-form-preview"]/section/div/button')))
        plan_journey.click()
    except TimeoutException:
        print("Timeout when clicking plan your journey")


def get_user_input():
    departure_location = input("Please enter your departure location: ")
    destination_location = input("Please enter your destination location: ")
    choose_date = input("Please enter your departure date: ")
    choose_hour = input("Please enter your departure time: ")
    passenger_number_adult = input("How many adult passengers are there?: ")
    passenger_number_child = input("How many child passengers are there?: ")
    railcard = input("Which railcard do you have?").upper()
    return departure_location, destination_location, choose_date, choose_hour, passenger_number_adult, passenger_number_child, railcard


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


def input_locations(driver, departure_location, destination_location):
    # Wait for element to be clickable
    try:
        departure_input = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "jp-origin"))
        )
        departure_input.clear()
        departure_input.send_keys(departure_location)
        print("Departure location entered:", departure_location)
        #Input locations using nlp
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
        time.sleep(2)

        # Clear input field
        driver.execute_script("arguments[0].value = '';", date_input)
        date_input.clear()
        time.sleep(2)

        # Attempt to set the date using JavaScript
        driver.execute_script(f"arguments[0].value = '{choose_date}';", date_input)
        time.sleep(2)

        # Verify if the date has been set correctly
        current_value = date_input.get_attribute('value')
        if current_value == choose_date:
            print("Date inserted successfully:", choose_date)
        else:
            # Use to sending keys if JavaScript isnt working
            date_input.click()
            date_input.clear()
            date_input.send_keys(choose_date)
            print("Date inserted via send_keys:", choose_date)

            # Check to see if the date is set correctly
            current_value = date_input.get_attribute('value')
            if current_value == choose_date:
                print("Date inserted successfully via send_keys:", choose_date)
            else:
                print(f"Failed to insert date. Current value: {current_value}")

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


def select_adults(driver, passenger_number):
    try:
        adults = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, 'adults')))
        select = Select(adults)
        select.select_by_value(str(passenger_number))
        time.sleep(2)
        print("Adult passengers entered:", passenger_number)
    except TimeoutException:
        print("Timeout occurred waiting for passenger input")
    except Exception as e:
        print("Error occurred while inputting passengers:", e)


def select_children(driver, passenger_number):
    try:
        children = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, 'children')))
        select = Select(children)
        select.select_by_value(str(passenger_number))
        time.sleep(2)
        print("Child passengers entered:", passenger_number)
    except TimeoutException:
        print("Timeout occurred waiting for passenger input")
    except Exception as e:
        print("Error occurred while inputting passengers:", e)

def add_railcard(driver,railcard):
    try:
        railcard_button = WebDriverWait(driver,20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="jp-form"]/section/div[5]/div/div/button')))
        railcard_button.click()
        time.sleep(2)

        select_railcard = WebDriverWait(driver,20).until(
            EC.presence_of_element_located((By.ID, 'railcard-0' ))
        )

        select = Select(select_railcard)

        select.select_by_value(railcard)
        print(f"selected railcard with value: {railcard}")

    except TimeoutException:
        print('timeout occurred whilst waiting')
    except Exception as e:
        print('error occurred:', e)




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
        click_no = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="fsrInvite"]/section[3]/button[2]')))
        time.sleep(3)
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


def main():
    driver = webdriver.Chrome()
    driver.get("https://www.nationalrail.co.uk")
    click_cookie(driver)
    click_journey(driver)
    # Get user input for departure and destination locations

    # departure_location, destination_location,choose_date,choose_hour = get_user_input()

    #departure_location, destination_location, choose_date, choose_hour = departure, destination, date, hour


    departure_location, destination_location,choose_date,choose_hour, passenger_number_adult, passenger_number_child, railcard = get_user_input()

    # Input locations on the webpage
    input_locations(driver, departure_location, destination_location)
    # Input departure time
    input_departure_date(driver, choose_date)
    time.sleep(3)
    select_departure_hour(driver, choose_hour)
    select_adults(driver, passenger_number_adult)
    select_children(driver, passenger_number_child)
    add_railcard(driver, railcard)
    click_show_trains(driver)
    time.sleep(1)
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
