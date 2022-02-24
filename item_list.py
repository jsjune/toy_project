import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime

client = MongoClient('mongodb+srv://test:sparta@cluster0.tfnms.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.toy_project

headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get('https://www.shoeprize.com/drops/', headers=headers)
soup = BeautifulSoup(data.text, 'html.parser')

items = soup.select('ul.calendar_list > li')

def crawling():
    for item in items:
        image = item.select_one('div.img_area > img')['data-src'].strip()
        brand = item.select_one('div.info_area > div.product_info > div.brand').text.strip()
        product_name = item.select_one('div.info_area > div.product_info > div.name').text.strip()
        draw_month = item.select_one('div.info_area > div.date_info > span.month').text.strip()
        draw_date = item.select_one('div.info_area > div.date_info > span.date').text.strip()
        doc = {
            'image': image,
            'brand': brand,
            'product_name': product_name,
            'draw_month': draw_month,
            'draw_date': draw_date
        }

        if db.items.find_one({'product_name': product_name}) is None:
            db.items.insert_one(doc)

    items_list = list(db.items.find({}))
    current_month = datetime.now().month
    current_date = datetime.now().day

    for item in items_list:
        month = item['draw_month']
        date = item['draw_date']
        if month == 'Jan':
            month = 1
        elif month == 'Feb':
            month = 2
        elif month == 'Mar':
            month = 3
        elif month == 'Apr':
            month = 4
        elif month == 'May':
            month = 5
        elif month == 'Jun':
            month = 6
        elif month == 'Jul':
            month = 7
        elif month == 'Aug':
            month = 8
        elif month == 'Sep':
            month = 9
        elif month == 'Oct':
            month = 10
        elif month == 'Nov':
            month = 11
        elif month == 'Dec':
            month = 12

        if month < current_month:
            db.items.delete_one({'_id': item['_id']})
        elif month == current_month:
            if date == '-':
                continue
            elif int(date) < current_date:
                db.items.delete_one({'_id': item['_id']})