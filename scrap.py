# selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import chromedriver_autoinstaller
import undetected_chromedriver as uc
import json

lenPage = 20
options = uc.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
options.add_argument('--no-sandbox')
# proxy http 
# options.add_argument('--proxy-server=http://lastlnwhacker0gaCH:PGdrLEdjKH@154.16.83.129:59100')
# fake user agent
options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' + '(KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36')   
driver = uc.Chrome(options=options, executable_path=chromedriver_autoinstaller.install())

def scarpUrl():
    url = []
    #find

    # for 1 - lenPage
    for i in range(1, lenPage+1):
        driver.get("http://www.resource.lib.su.ac.th/awardsu/web/type.php?option=&keyword=จิตรกรรม&page=" + str(i))
        while True:
            try:
                driver.find_element(By.CSS_SELECTOR, ".info.Sriracha")
                break
            except:
                pass
        x = driver.find_elements(By.CSS_SELECTOR, ".info.Sriracha")
        for i in x:
            url.append(i.get_attribute('href'))

        print(len(url))

        # remove duplicate url
        url = list(dict.fromkeys(url))

    print(url)

    # save url to file
    with open('url.txt', 'w') as f:
        for item in url:
            f.write("%s\n" % item)


def scrapInfo():
    # schema
    # {
    #     "Artwork_Name": "",
    #     "Artist_Name": "",
    #     "Artwork_Type": "",
    #     "Artwork_Size": "",
    #     "Artwork_Technique": "",
    #     "Exhibition_Name": "",
    #     "Award_Name": "",
    #     "License": "",
    #     "Concept": "",
    #     "Detail": "",
    #     "Image": "",
    #     "URL": ""
    # }

    # Read the URLs from the file
    with open('url.txt', 'r') as f:
        urls = [line.strip() for line in f.readlines()]

    # Define a dictionary to map data fields to XPaths
    data_fields = {
        "Artwork_Name": '//mark[@class="title" and text()="ชื่อผลงาน"]/following-sibling::span',
        "Artist_Name": '//mark[@class="title" and text()="ชื่อศิลปิน"]/following-sibling::span',
        "Artwork_Type": '//mark[@class="title" and text()="ประเภท"]/following-sibling::span',
        "Artwork_Size": '//mark[@class="title" and text()="ขนาด"]/following-sibling::span',
        "Artwork_Technique": '//mark[@class="title" and text()="เทคนิค"]/following-sibling::span',
        "Exhibition_Name": '//mark[@class="title" and text()="นิทรรศการ"]/following-sibling::span',
        "Award_Name": '//mark[@class="title" and text()="รางวัลที่ได้รับ"]/following-sibling::span',
        "License": '//mark[@class="title" and text()="ผู้ครอบครอง"]/following-sibling::span',
        "Concept": "//*[@id='concept']/span",
        "Detail": "//*[@id='description']/span",
        "Image": "//img[@class='img-responsive']",
        "URL": ""
    }

    data = []

    # delete p tag that not have text
    p_elements = driver.find_elements(By.XPATH, "//p[text()='']")
    for p_element in p_elements:
        driver.execute_script("arguments[0].remove();", p_element)

    # Scrape the data from each URL
    for url in urls:
        print("Scraping:", url)
        driver.get(url)
        scraped_data = {}
        # click button
        try:
            x = driver.find_elements(By.CSS_SELECTOR, ".btn.btn-primary")
            for i in x:
                i.click()
        except:
            pass
        for field, xpath in data_fields.items():
            try:
                if field == "URL":
                    scraped_data[field] = url
                    continue
                element = driver.find_element(By.XPATH, xpath)
                if field == "Image":
                    scraped_data[field] = element.get_attribute('src')
                else:
                    scraped_data[field] = element.text
            except Exception as e:
                print("Error processing field:", field)
                scraped_data[field] = ""
        data.append(scraped_data)

    # Save the scraped data to a JSON file
    with open('data.json', 'w') as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=4)

    # Close the WebDriver when done
    driver.quit()

scrapInfo()
