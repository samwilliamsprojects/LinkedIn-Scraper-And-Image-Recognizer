from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import time
from datetime import datetime

import pandas as pd
import os
import requests
import io
from PIL import Image
import cv2
from gender_identifier import predict_gender


# LOGIN INFO
EMAIL = 'YOUR EMAIL'
PASSWORD = 'YOUR PASSWORD'

# use phone number login?
# PHONE_NUMBER = 'YOUR PHONE NUMBER'

# CONSTANTS
DESIRED_NUM_PEOPLE = 100
PAGES = DESIRED_NUM_PEOPLE / 10 # 10 people are shown on each page

# directory for saved images
DIRECTORY = 'saved_images_directory'

# Selenium setup
driver_path = "YOUR DRIVER PATH"
driver = webdriver.Chrome(driver_path)

# Navigates to linkedin
driver.get('https://www.linkedin.com/')
time.sleep(3)

# maximizes window
driver.maximize_window()

# inputs email and password to sign in
email_section = driver.find_element(By.ID, 'session_key')
email_section.send_keys(EMAIL)
password_section = driver.find_element(By.ID, 'session_password')
password_section.send_keys(PASSWORD)
password_section.send_keys(Keys.ENTER)
time.sleep(3)

# Finds desired company
search_bar = driver.find_element(By.XPATH, '''//*[@id="global-nav-typeahead"]/input''')
search_bar.click()
search_bar.send_keys('DESIRED_COMPANY_NAME people')
search_bar.send_keys(Keys.ENTER)
time.sleep(3)

# Navigates to 'people' section
all_results = driver.find_element(By.LINK_TEXT, "See all people results")
all_results.click()
time.sleep(2)

# function to get names, titles, and locations of all people showing. Each page shows 10 people at a time
def get_info():
    names_list = []
    titles_list = []
    locations_list = []

    # Locates name, title and location from profiles
    all_names = driver.find_elements(By.CSS_SELECTOR, '.entity-result__title-text')
    all_titles = driver.find_elements(By.CSS_SELECTOR, '.entity-result__primary-subtitle')
    all_locations = driver.find_elements(By.CSS_SELECTOR, '.entity-result__secondary-subtitle')

    # Name is returned with extra info; must only take first and last name
    for name in all_names:
        unclean_name = name.text
        clean_name = unclean_name.splitlines()[0]
        names_list.append(clean_name)

    for title in all_titles:
        titles_list.append(title.text)

    for location in all_locations:
        locations_list.append(location.text)

    # Finds all photos
    photos = driver.find_elements(By.CSS_SELECTOR, '.ivm-view-attr__img--centered.EntityPhoto-circle-3')
    time.sleep(0.1)

    # photos are accessed by a url, use the 'src' attribute for this
    for i in photos:
        photo_url = i.get_attribute('src')
        image_content = requests.get(photo_url).content

        # filename saves it by time, allowing the list of files to be in order with other lists
        file_name = datetime.utcnow().strftime('%Y%m%d%H%M%S%f.jpg')
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file).convert('RGB')

        # determines file path for photos to be saved
        file_path = os.path.join(DIRECTORY, file_name)

        # saves image
        with open(file_path, 'wb') as f:
            image.save(f, "JPEG", quality=85)
            time.sleep(0.1)

    return names_list, titles_list, locations_list


# scrolls to the bottom of the page and clicks "Next"
def next_page():
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(1)
    next_button = driver.find_element(By.CSS_SELECTOR, ".artdeco-pagination__button--next")
    next_button.click()


first_names = []
last_names = []
total_titles = []
total_locations = []

# Loop to call the functions as many times as needed and combine their information into lists
for page in range(int(PAGES)):
    name, title, location = get_info()
    # splits names into first and last
    for n in name:
        first = n.split(" ")[0]
        last_list = n.split(" ")[1:]
        # joins all last names or titles (such as "MBA") instead of embedding an extra list
        last = " ".join(last_list)
        first_names.append(first)
        last_names.append(last)
    for t in title:
        total_titles.append(t)
    for l in location:
        total_locations.append(l)
    time.sleep(1)
    next_page()
    time.sleep(2)

gender_list = []

# iterates through all images
for image_path in os.listdir('saved_images'):

    # ignores hidden files
    if image_path.endswith(".jpg"):
        # reads image using cv2 package
        ima = cv2.imread(f'saved_images/{image_path}')

        # predicts gender
        gen = predict_gender(ima)

        # adds gender in order to list
        gender_list.append(gen)


# saves all personal info to a csv file
df = pd.DataFrame(data={"First names": first_names, "Last names": last_names,
                        "Label": total_titles, "Location": total_locations})
df.to_csv(path_or_buf="info_csv", sep=",", index=False)

# separate list for gender identifications, as image list is shorter due to missing profile pictures
gender_df = pd.DataFrame(data={'Gender': gender_list})
gender_df.to_csv(path_or_buf="gender_csv", sep=',', index=True)