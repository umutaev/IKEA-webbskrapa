from selenium import webdriver

with open('chromedriver_path', encoding='utf8') as f:
    chromedriver_path = f.read()

contents_url = "https://www.ikea.com/us/en/cat/series-series/"


def contents_url_parser(driver: webdriver.Chrome, url):
    driver.get(url)
    items = {}
    for li in driver.find_element_by_class_name("vn__textnav__fifteen-and-up").find_elements_by_tag_name('li'):
        items[li.find_element_by_tag_name('a').find_element_by_tag_name('span').text] = \
            li.find_element_by_tag_name('a').get_attribute('href')
    driver.close()
    return items


def sub_page_scrapper(driver: webdriver.Chrome, url):
    driver.get(url)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    items = {}
    for div in driver.find_elements_by_class_name('plp-fragment-wrapper'):
        item_desc = div.find_element_by_class_name('range-revamp-header-section__description-text').text
        if item_desc in items:
            items[item_desc].append(div.find_element_by_tag_name('a').get_attribute('href'))
        else:
            items[item_desc] = [div.find_element_by_tag_name('a').get_attribute('href')]
    driver.close()
    return items
    # print(soup.find_all('div', class_='plp-fragment-wrapper')[0].find('a')['href'])


if __name__ == "__main__":
    driver = webdriver.Chrome(chromedriver_path)
    print(contents_url_parser(driver, contents_url))
    # print(sub_page_scrapper(driver, 'https://www.ikea.com/us/en/cat/lidhult-series-41941/?page=1000'))
