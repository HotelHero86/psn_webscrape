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
    
my_url = "https://store.playstation.com/en-us/category/3f772501-f6f8-49b7-abac-874a88ca4897/1"

def getPageHTML(url):
    "opening connection and grabbing the first page, returns a page_soup"
    uClient = uReq(url)
    page_html = uClient.read()
    uClient.close()

    return soup(page_html, "html.parser")

def sort_by_price(game):
    return str(game.sale_price)

# get all the containers from the page listing the sales
containers = getPageHTML(my_url).findAll("div", {"class": "psw-product-tile psw-interactive-root"})
links = []

#pull the URL links for each sale page
for container in containers:
    link = container.find("a", {"class" : "internal-app-link ember-view"})
    links.append(link)


#grab each sale page that is linked
sale_pages = []

for link in links:
    sale_page = getPageHTML("https://store.playstation.com" + link["href"]) # + "/1?gameContentType=games%2Cbundles%2Caddons")
    sale_pages.append(sale_page)

#add each page after the first to the sale_page list
for sale_page in sale_pages:
    nextpage = sale_page.find("a", {"class" : "psw-icon psw-icon--chevron-right psw-icon psw-icon-size2 psw-icon--chevron-right"})
    if nextpage is not None:
        sale_pages.append(getPageHTML(my_url + nextpage["href"]))

#creating the list of games
games = []

#iterate through each sale page that was grabbed
for sale_page in sale_pages:

    cells = sale_page.findAll("div", {"class" : "psw-product-tile psw-interactive-root"})
    #from every cell, make a game object with its name and prices and add it to a list
    for cell in cells:

        title = cell.find("span").getText()
        if cell.find("span", {"data-qa" : "ems-sdk-grid#productTile0#price#display-price"}) is None:
            reg_price = "0.00"
        else:
            reg_price = float(cell.find("data-qa" : "ems-sdk-grid#productTile0#price#display-price").getText().replace("$",""))
        if cell.find("h3", {"data-qa" : "ems-sdk-grid#productTile0#price#display__price"}) is None:
            sale_price = "0.00"
        else: 
            sale_price = float(cell.find("h3", {"data-qa" : "ems-sdk-grid#productTile0#price#display__price"}).getText().replace("$",""))

        games.append(game(title, sale_price, reg_price))

        
games.sort(reverse=True,key=sort_by_price)

#adding the list to a csv file named for today's date
date = str(datetime.today().strftime("%b-%d-%Y"))
textfilename = "D:\python\psnscraper\games" + date + ".txt"
csvfilename = "D:\python\psnscraper\games" + date + ".csv"

f2 = open(csvfilename, "w")
f2.write("Title,Sale Price,Regular Price\n")
for x in games:
    try:
        f2.write("{},${},${}\n".format(x.title.replace(",","|").replace("\t","").replace(";","|"), str(x.sale_price), str(x.regular_price)))
    except:
        continue

f2.close()
"""
date = str(datetime.today().strftime("%b%d%Y"))
conn = db.connect('psn.db')
conn.row_factory = db.Row
cursor = conn.execute('select * from PSN_PRICE_TRACKING')
row = cursor.fetchone()
names = row.keys()

for name in names:
    if name is date:
        exit
    
cursor = conn.execute("ALTER TABLE PSN_PRICE_TRACKING ADD COLUMN {};".format(date))

game_list = cursor.fetchall(cursor.execute("select name from table;"))

for game in games:
    game_name = str(game.title.replace('\'',"").replace('\"',"").replace(",","|").replace("\t","").replace(";","|"))
    cursor.execute("INSERT INTO PSN_PRICE_TRACKING VALUES({}, '{}', {}, {});".format(name , game.regular_price, game.sale_price))
    print("record inserted")

#cursor.execute("create TABLE PSN_PRICE_TRACKING (gameID INTEGER PRIMARY KEY, name TEXT, regular_price INTEGER, {0} smallint INTEGER)".format(date))
#print("Table created")


#i = 0

#for game in games:
#    i = i + 1
#    name = str(game.title.replace('\'',"").replace('\"',"").replace(",","|").replace("\t","").replace(";","|"))
#    cursor.execute("INSERT INTO PSN_PRICE_TRACKING VALUES({}, '{}', {}, {});".format(i, name , game.regular_price, game.sale_price))
#    print("record inserted")


    
cursor.execute("SELECT * FROM PSN_PRICE_TRACKING")
print(cursor.fetchall())
conn.commit()   
cursor.close
 
"""
