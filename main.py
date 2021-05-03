import bs4
import requests

contents_url = "https://www.ikea.com/us/en/cat/series-series/"


def contents_url_parser(url):
    response = requests.get(url)
    if not response.status_code == requests.codes.ok:
        raise ConnectionError  # TODO: handling
    html = response.content.decode('utf-8')
    soup = bs4.BeautifulSoup(html, 'html.parser')
    items = []
    for li in soup.find('ul', class_='vn__textnav__fifteen-and-up').find_all('li'):
        items.append({li.a.span.text: li.a['href']})
    return items


if __name__ == "__main__":
    print(*contents_url_parser(contents_url), sep='\n')
