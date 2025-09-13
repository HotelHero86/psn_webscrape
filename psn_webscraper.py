from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
from datetime import datetime
import sqlite3 as db


class game:
    def __init__(self, title, sale_price, regular_price):
        self.title = title
        self.sale_price = sale_price
        self.regular_price = regular_price

    def __str__(self):
        return self.title + " " + self.sale_price + " " + self.regular_price
    
my_url = "https://store.playstation.com/en-us/category/3f772501-f6f8-49b7-abac-874a88ca4897/"

def getPageHTML(url):
    "opening connection and grabbing the first page, returns a page_soup"
    uClient = uReq(url)
    page_html = uClient.read()
    uClient.close()

    return soup(page_html, "html.parser")

#still need to find a way to calculate the number of pages
#rather than hardcode
number_of_pages = 150


#grab each sale page
sale_pages = []

while number_of_pages >= 1:
    sale_page = getPageHTML(my_url)
    sale_page = getPageHTML(my_url + str(number_of_pages))
    sale_pages.append(sale_page)
    number_of_pages = number_of_pages - 1

#creating the list of games
games = []

#iterate through each sale page that was grabbed
for sale_page in sale_pages:

    cells = sale_page.find_all("div", {"class" : "psw-product-tile psw-interactive-root"})
    #from every cell, make a game object with its name and prices and add it to a list
    for cell in cells:

        title = cell.find("span").getText()
        if cell.find("span", {"data-qa" : "ems-sdk-grid#productTile" + str(cells.index(cell)) + "#price#display-price"}) is None:
            sale_price = "0.00"
        else:
            sale_price = float(cell.find("span", {"data-qa" : "ems-sdk-grid#productTile" + str(cells.index(cell)) + "#price#display-price"}).getText().replace("$",""))
        if cell.find("s", {"data-qa" : "ems-sdk-grid#productTile" + str(cells.index(cell)) + "#price#price-strikethrough"}) is None:
            reg_price = "0.00"
        else: 
            reg_price = float(cell.find("s", {"data-qa" : "ems-sdk-grid#productTile" + str(cells.index(cell)) + "#price#price-strikethrough"}).getText().replace("$",""))

        games.append(game(title, sale_price, reg_price))

#adding the list to a csv file named for today's date
date = str(datetime.today().strftime("%b-%d-%Y"))
textfilename = "PSNScrapedGames" + date + ".txt"
csvfilename = "PSNScrapedGames" + date + ".csv"

#write to .csv file
f2 = open(csvfilename, "w")
f2.write("Title,Sale Price,Regular Price,Sale Percentage\n")
for x in games:
    try:
        f2.write("{},${},${},{}%\n".format(x.title.replace(",","|").replace("\t","").replace(";","|"), str(x.sale_price), str(x.regular_price), str(int(100 * (1 -(x.sale_price / x.regular_price))))))
    except:
        continue

f2.close()
