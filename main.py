import bs4
import requests

chromedriver_path = 'c:\\Users\\max\\Documents\\IKEA-webbskrapa\\lib\\chromedriver_90.0.4430.24.exe'

contents_url = "https://www.ikea.com/us/en/cat/series-series/"


def contents_url_parser(url):
    response = requests.get(url)
    if not response.status_code == requests.codes.ok:
        raise ConnectionError  # TODO: handling
    html = response.content.decode('utf-8')
    soup = bs4.BeautifulSoup(html, 'html.parser')
    items = {}
    for li in soup.find('ul', class_='vn__textnav__fifteen-and-up').find_all('li'):
        items[li.a.span.text] = li.a['href']
    return items


def sub_page_scrapper(url):
    response = requests.get(url)
    print(response.text[-50:])
    if not response.status_code == requests.codes.ok:
        raise ConnectionError  # TODO: handling
    html = response.content.decode('utf-8')
    soup = bs4.BeautifulSoup(html, 'html.parser')
    items = {}
    temp = soup.find_all('div', class_='plp-fragment-wrapper')
    for div in temp:
        item_description = div.find('span', class_='range-revamp-header-section__description-text').text
        if item_description in items:
            items[item_description].append(div.find('a')['href'])
        else:
            items[item_description] = [div.find('a')['href']]
    return items
    # print(soup.find_all('div', class_='plp-fragment-wrapper')[0].find('a')['href'])


if __name__ == "__main__":
    print(sub_page_scrapper('https://www.ikea.com/us/en/cat/lidhult-series-41941/?page=1000'))
    # print(sum(len(lst) for lst in sub_page_scrapper('https://www.ikea.com/us/en/cat/lidhult-series-41941/?page=1000').values()))
