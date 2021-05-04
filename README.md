# IKEA WEBBSKRAPA
This project was inspired by the IKEA article system and the lack of keyed catalogs. So, I decided to create not only the catalog but something, that can keep it updated.

## Requirements
Now you can install everything you need via requirements.txt file. `pip install -r requirements.txt` 
However, you anyway have to install Chrome browser manually.


## Usage
Specify chromedriver path in chromedriver_path file or in main_on_selenium.py constants section.

Run `main_on_selenium.py` and wait until it parse everything.
It takes a lot of time, so my recommendation is to use remote server with Xvfb.
Note that selenium use X-server while run, so it'll open and close a bunch of Chrome automatically.

Personally, I don't recommend running it on macOS because there were some issues regarding selenium on macOS.

## TODO
- [x] Contents page scrapper
- [x] Series page scrapper
- [x] Items page scrapper
- [x] Database writing
- [ ] Some kind of api
- [ ] .xlsx export
- [x] Add requirements.txt
