import requests
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
import re
import config

DESIRED_DAY = "火" # Day to monitor. In my case, only available time is Saturday.
DESIRED_ACCOMODATION = "毛無山荘" # Accomodation to monitor.

opts = FirefoxOptions()
opts.add_argument("--headless")
driver = webdriver.Firefox(options=opts)
driver.get('https://fumotoppara.secure.force.com/RS_Top')

select = Select(driver.find_element(By.ID,'f_nengetsu'))

# Select by visible text
available_dates = ""
for index in range(len(select.options)):
    select.select_by_index(index)
    select = Select(driver.find_element(By.ID,'f_nengetsu'))
    year_month = select.first_selected_option.text
    table = driver.find_element(By.CLASS_NAME, "tbl_frame")

    # Find wished accomodation index
    accomodation_index = [m.start() for m in re.finditer(DESIRED_ACCOMODATION, table.text)][0]
    start_index= re.search(DESIRED_ACCOMODATION, table.text).start()
    header = table.text[:table.text.find("\n", start_index)].split(" ")
    try : 
        accomodation_index = header.index(DESIRED_ACCOMODATION)
    except:
        print("Please confirm the accomodation plan !")

    all_selected_days = [m.start() for m in re.finditer(DESIRED_DAY, table.text)]
    for s in all_selected_days:
        start_row = table.text[:s].rfind("\n")
        row_content = year_month + table.text[start_row+1:s+9]
        availabilities_all = table.text[start_row+1:s+9].split(" ")
        availability_for_desired_accomodation = availabilities_all[accomodation_index]
        # ○ and △ corresponds to availabilities
        if availability_for_desired_accomodation == "○" or availability_for_desired_accomodation == "△": 
            available_dates += row_content 
            available_dates += "\n"

# If some dates are available, send a message to Telegram
if available_dates != "":
    query = {'chat_id':'959302993', 'text':'Fumotoppara reservation !'+"\n" + available_dates} 
    response = requests.get(config.telegram_bot_url, params=query) 

