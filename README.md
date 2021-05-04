# IKEA WEBBSKRAPA
This project was inspired by IKEA article system, and the lack of keyed catalogs. 
So, I decided to create not only the catalog, but something, that can keep it updated.

## Requirements
I haven't made a requirements.txt yet, so, to run my code you need:
1. BeautifulSoup
2. Requests
3. Selenium
4. Chrome web browser
5. Chrome web driver

## Usage
Run `main_on_selenium.py` and wait until it parse everything.
Note that selenium use X-server while run, so it'll open and close a bunch of Chrome automatically.

## TODO
- [x] Contents page scrapper
- [x] Series page scrapper
- [x] Items page scrapper
- [x] Database writing
- [ ] Some kind of api
- [ ] .xlsx export
