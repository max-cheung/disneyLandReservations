import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv

# prevents chrome and chromedriver from closing at the end
options = Options()
options.add_experimental_option("detach", True)

# access dotenv variables
load_dotenv()
email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")
phoneNumber1 = os.getenv("PHONENUMBER1")
phoneNumber2 = os.getenv("PHONENUMBER2")

# reservation details
reservationMonth = 'April'
reservationDay = '14'
reservationTime = 'Dinner'

driver = webdriver.Chrome(options=options)
driver.get("https://disneyland.disney.go.com/login?appRedirect=%2F")

# switch to iframe
driver.switch_to.frame("disneyid-iframe")

# enter email
emailElement = driver.find_element(By.XPATH, '//input[@type="email"]')
emailElement.send_keys(email)

# enter password
passwordElement = driver.find_element(By.XPATH, '//input[@type="password"]')
passwordElement.send_keys(password)

# sign in
signinElement = driver.find_element(By.CLASS_NAME, 'btn.btn-primary.btn-submit.ng-isolate-scope')
signinElement.click()
time.sleep(10)

# confirm signin successfull before proceeding to reservation page
try:
    loggedInElement = WebDriverWait(driver, 300).until(
        EC.presence_of_element_located((By.XPATH, '//a[contains(@class, "signOut")]'))
    )
finally:
    driver.get("https://disneyland.disney.go.com/dining/disney-california-adventure/lamplight-lounge/availability-modal")

# confirm reservation popup is present before clicking on calendar selection
try:
    makeReservationElement = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, 'modal-title-1'))
    )
finally:
    calendarElement = driver.find_element(By.XPATH, '/html/body/finder-modal[2]/div[1]/div/div/div[2]/finder-availability-modal/div/div[1]/finder-date-picker-wrapper/div/button/div[1]/finder-input')
    calendarElement.click()

# next month calendar element
nextMonthElement = driver.find_element(By.XPATH, '/html/body/finder-modal[2]/div[1]/div/div/div[2]/finder-availability-modal/div/div[1]/finder-date-picker-wrapper/div/finder-calendar/div/div[1]/a/finder-font-icon/span')

# checks month selected
monthElement = driver.find_element(By.XPATH, '(//span[contains(@class, "month-name")])[2]')
month = monthElement.text

# clicks until desired month is selected
while month != reservationMonth :
    nextMonthElement.click()
    #obtains current month selected
    monthElement = driver.find_element(By.XPATH, '(//span[contains(@class, "month-name")])[2]')
    month = monthElement.text
    print(month)

# clicks on the desired reservation date
allDateElement = driver.find_elements(By.XPATH, '//finder-modal//td/a[contains(@class, "cell")]')

for date in allDateElement:
    data=date.text
    if data == reservationDay :
        print(data)
        date.click()
        break

# manual keypresses to obtain reservation time of "dinner" due to shadow-root
timeElement = driver.find_element(By.CSS_SELECTOR, 'wdpr-single-select')
timeElement.click()
time.sleep(1)
timeElement.send_keys(Keys.ARROW_DOWN)
time.sleep(.5)
timeElement.send_keys(Keys.ARROW_DOWN)
time.sleep(.5)
timeElement.send_keys(Keys.RETURN)

# manual keypresses to obtain party size of 3 due to shadow-root
partySizeElement = driver.find_element(By.XPATH, '//label[@for="partySizeCounter"]')
partySizeElement.click()
actions = ActionChains(driver)
actions.send_keys(Keys.TAB)
actions.send_keys(Keys.TAB)
actions.send_keys(Keys.RETURN)
actions.perform()

# search times
searchElement = driver.find_element(By.ID, 'search-time-button')
searchElement.click()
time.sleep(3)

# prints initial unavailability
unavailableElement = driver.find_element(By.XPATH, '//div[contains(@class, "times-unavailable")]')
print(unavailableElement.text)

# response variable initialized
sorryMessageElement = driver.find_element(By.XPATH, '//div[contains(@class, "times-unavailable")]//div[contains(@class, "head")]')
response = sorryMessageElement.text

# while loop to check availability every 60 seconds
while response == 'Sorry!' :
    searchElement.click()
    time.sleep(3)
    sorryMessageElement = driver.find_element(By.XPATH, '//div[contains(@class, "times-unavailable")]//div[contains(@class, "head")]')
    response = sorryMessageElement.text
    ts = time.time()
    date_time = datetime.fromtimestamp(ts)
    print(date_time, 'No Availability')
    time.sleep(57)

# alerts to notify availability
ts = time.time()
date_time = datetime.fromtimestamp(ts)
print(date_time, 'Available!!')

# iMessage alerts
message = "\"Lamplight Lounge available on {} {} for {}!!\"".format(reservationMonth, reservationDay, reservationTime)
os.system(
    "osascript sendMessage.applescript {} {}"
        .format(phoneNumber1, message)
)
os.system(
    "osascript sendMessage.applescript {} {}"
        .format(phoneNumber2, message)
)
print('iMessage Sent!')