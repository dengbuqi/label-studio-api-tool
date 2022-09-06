
from selenium import webdriver
# import chromedriver_autoinstaller
# chromedriver_autoinstaller.install()
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
PROJECT_NAME = 'Nave_Image_30cls'

# Start registering
s=Service('./chromedriver')
# s = Service()
browser = webdriver.Chrome(service=s)
url='http://127.0.0.1:8080/user/login/'
browser.get(url)
userid = browser.find_element(By.ID, 'email')
pwd = browser.find_element(By.ID, 'password')
btn = browser.find_element(By.CLASS_NAME,'ls-button_look_primary')
userid.send_keys("1@qq.com")
pwd.send_keys("deng@199451")
btn.click()
time.sleep(1)
# try:
projcts = browser.find_elements(By.CSS_SELECTOR, '.ls-projects-page__link')
for pjt in projcts:
    div = pjt.find_element(By.CSS_SELECTOR, '.ls-project-card__title-text')
    if div.text == PROJECT_NAME:
        pjt.click()
        break
time.sleep(2)

body = browser.find_element(By.CSS_SELECTOR, '.dm-table__virual')
data_id = set()
# data = browser.find_elements(By.CSS_SELECTOR, '.dm-table-row')
data = browser.find_elements(By.XPATH,'//div[@class="dm-table-row dm-table-row"]/div[2]')
for row in data:
    data_id.add(row.text)
temp_height = 0
while True:
    browser.execute_script(f"arguments[0].scrollBy(0,1000);", body)
    check_height = browser.execute_script("return arguments[0].scrollTop;", body)
    if check_height == temp_height:
        break
    data = browser.find_elements(By.XPATH,'//div[@class="dm-table-row dm-table-row"]/div[2]')
    for row in data:
        data_id.add(row.text)
    temp_height = check_height
    print('page down', check_height)
    temp_height=check_height
    time.sleep(0.2) #delay

for id in sorted(list(data_id)):
    print(id)
    # browser.get(f'http://127.0.0.1:8080/projects/24/data?tab=19&task={id}')
    # time.sleep(0.5)

browser.quit()