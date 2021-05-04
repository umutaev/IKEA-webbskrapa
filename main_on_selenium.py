import sqlite3

import selenium.common.exceptions
from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import logging

logging.basicConfig(filename='log.txt', filemode='a')

chromedriver_path = None
chromedriver_path_file = "chromedriver_path"
contents_url = "https://www.ikea.com/us/en/cat/series-series/"  # Main contents IKEA page


def contents_url_parser(url, database_connection: sqlite3.Connection = None):
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    if database_connection:
        cursor = database_connection.cursor()
    items = {}
    for li in soup.find(class_="vn__textnav__fifteen-and-up").find_all('li'):
        key = li.find('a').find('span').text  # Series name
        item = li.find('a')['href']  # Series link
        items[key] = item
        if database_connection:
            cursor.execute(f"INSERT INTO Series (name, link) SELECT '{key}', '{item}' "
                           f"WHERE NOT EXISTS (SELECT * FROM Series WHERE name = '{key}' AND link = '{item}')")
    if database_connection:
        database_connection.commit()  # Write to DB if possible
    logging.info("Contents page parsed")
    return items


def sub_page_scrapper(url):
    driver = webdriver.Chrome(chromedriver_path)  # Here we need selenium because page is loading dynamically
    driver.get(url)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Scroll to bottom
    items = []
    for div in driver.find_elements_by_class_name('plp-fragment-wrapper'):
        items.append(div.find_element_by_tag_name('a').get_attribute('href'))  # Append link to a product
    driver.close()
    return items


def item_page_scrapper(url):
    base = BeautifulSoup(requests.get(url).content, 'html.parser')
    variants = [i.get('href') for i in base.find_all("a", class_="range-revamp-product-styles__item")
                if i.get('href') is not None]  # Find all possible variants of one product
    soup_list = [base]
    item = []
    for variant in variants:
        soup_list.append(BeautifulSoup(requests.get(variant).content, 'html.parser'))
        # Append scrapping instances for each variant
    for soup in soup_list:
        description = soup.find('span', class_='range-revamp-header-section__description-text').text
        # Description of an item, including name and color
        try:
            img_urls = [div.find('img').get('src').split('?')[0] for div in
                        soup.find_all('div', class_='range-revamp-media-grid__media-container')]
            # URLs to images of current variant
        except AttributeError:
            img_urls = []
            # Sometimes layout can be different, but it's hard to catch and fix
        item.append({"description": description,
                     "price": float(
                         soup.find('span', class_='range-revamp-price').text.replace(',', '_').replace('$', '')
                             .split('/')[0]),  # Price of an item. Including cents
                     "article": soup.find('span', class_='range-revamp-product-identifier__value').text,
                     # Article number of an item. Very important thing in IKEA
                     "img_urls": img_urls})
    return item


if __name__ == "__main__":
    if chromedriver_path is None:
        try:
            with open(chromedriver_path_file, encoding='utf8') as f:
                chromedriver_path = f.read()  # Read chromedriver path if possible
        except FileNotFoundError:
            print("chromedriver_path file not found")
            exit(0)
    db = sqlite3.connect('result.db')
    # result.db is a file with parsed items
    cursor = db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS Series (id INTEGER PRIMARY KEY, name TEXT NOT NULL, link TEXT NOT NULL)")
    # Create table for series
    db.commit()
    contents_url_parser(contents_url, database_connection=db)
    cursor.execute("SELECT name, link FROM Series")
    # If database was updated and some values are gone. It'll try to parse everything
    db.commit()
    for series in cursor.fetchall()[19:20]:
        try:
            product_urls = sub_page_scrapper(series[1])
        except selenium.common.exceptions.InvalidArgumentException:
            logging.warning("Something went wrong with " + series[1] + " during selenium parsing")
            continue
        items = []
        for product in product_urls:
            items.extend(item_page_scrapper(product))
            # Merge all entries for every product variant
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {series[0].replace(' ', '')} "
                       f"(id INTEGER PRIMARY KEY AUTOINCREMENT, description TEXT NOT NULL, "
                       f"price REAL, article TEXT NOT NULL, picture_links TEXT)")
        # Create table for different series of products
        db.commit()
        for item in items:
            cursor.execute(f"INSERT INTO {series[0].replace(' ', '')} (description, price, article, picture_links) "
                           f"SELECT \"{item['description']}\", {item['price']}, \"{item['article']}\", "
                           f"\"{' '.join(item['img_urls'])}\" WHERE NOT EXISTS (SELECT * FROM "
                           f"{series[0].replace(' ', '')} WHERE description = \"{item['description']}\" AND "
                           f"price = {item['price']} AND "
                           f"article = \"{item['article']}\" AND "
                           f"picture_links = \"{' '.join(item['img_urls'])}\")")
            # Write description, price, article and img urls if it's not in db or differs
        logging.info(series[0] + " done")
        db.commit()
