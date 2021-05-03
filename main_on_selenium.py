import sqlite3
from selenium import webdriver
import requests
from bs4 import BeautifulSoup

with open('chromedriver_path', encoding='utf8') as f:
    chromedriver_path = f.read()

contents_url = "https://www.ikea.com/us/en/cat/series-series/"


def contents_url_parser(url, database_connection: sqlite3.Connection = None):
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    if database_connection:
        cursor = database_connection.cursor()
    items = {}
    for li in soup.find(class_="vn__textnav__fifteen-and-up").find_all('li'):
        key = li.find('a').find('span').text
        item = li.find('a')['href']
        items[key] = item
        if database_connection:
            cursor.execute(f"INSERT INTO Series (name, link) SELECT '{key}', '{item}' "
                           f"WHERE NOT EXISTS (SELECT * FROM Series WHERE name = '{key}' AND link = '{item}')")
    if database_connection:
        database_connection.commit()
    return items


def sub_page_scrapper(url):
    driver = webdriver.Chrome(chromedriver_path)
    driver.get(url)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    items = []
    for div in driver.find_elements_by_class_name('plp-fragment-wrapper'):
        items.append(div.find_element_by_tag_name('a').get_attribute('href'))
    driver.close()
    return items


def item_page_scrapper(url):
    base = BeautifulSoup(requests.get(url).content, 'html.parser')
    variants = [i.get('href') for i in base.find_all("a", class_="range-revamp-product-styles__item")
                if i.get('href') is not None]
    soup_list = [base]
    item = []
    for variant in variants:
        soup_list.append(BeautifulSoup(requests.get(variant).content, 'html.parser'))
    for soup in soup_list:
        description = soup.find('span', class_='range-revamp-header-section__description-text').text
        try:
            img_urls = [div.find('img').get('src').split('?')[0] for div in soup.find_all('div', class_='range-revamp-media-grid__media-container')]
        except AttributeError:
            img_urls = []
        item.append({"description": description,
                     "price": float(
                         soup.find('span', class_='range-revamp-price').text.replace(',', '_').replace('$', '')
                             .split('/')[0]),
                     "article": soup.find('span', class_='range-revamp-product-identifier__value').text,
                     "img_urls": img_urls})
    return item


if __name__ == "__main__":
    db = sqlite3.connect('result.db')
    cursor = db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS Series (id INTEGER PRIMARY KEY, name TEXT NOT NULL, link TEXT NOT NULL)")
    db.commit()
    contents_url_parser(contents_url, database_connection=db)
    cursor.execute("SELECT name, link FROM Series")
    db.commit()
    for series in cursor.fetchall()[141:143]:
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {series[0].replace(' ', '')} "
                       f"(id INTEGER PRIMARY KEY AUTOINCREMENT, description TEXT NOT NULL, "
                       f"price REAL, article TEXT NOT NULL, picture_links TEXT)")
        db.commit()
        items = []
        for product in sub_page_scrapper(series[1]):
            items.extend(item_page_scrapper(product))
        for item in items:
            cursor.execute(f"INSERT INTO {series[0].replace(' ', '')} (description, price, article, picture_links) "
                           f"SELECT \"{item['description']}\", {item['price']}, \"{item['article']}\", "
                           f"\"{' '.join(item['img_urls'])}\" WHERE NOT EXISTS (SELECT * FROM "
                           f"{series[0].replace(' ', '')} WHERE description = \"{item['description']}\" AND "
                           f"price = {item['price']} AND "
                           f"article = \"{item['article']}\" AND "
                           f"picture_links = \"{' '.join(item['img_urls'])}\")")
        db.commit()
