import requests
from bs4 import BeautifulSoup
import mysql.connector

# Gửi yêu cầu HTTP và lấy dữ liệu từ trang web
url = 'https://www.foody.vn/ho-chi-minh/an-vat-via-he'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Trích xuất dữ liệu cần thiết từ trang web
restaurants = []
for item in soup.find_all('div', class_='card-item'):
    name = item.find('div', class_='name').text.strip()
    address = item.find('div', class_='address').text.strip()
    restaurants.append((name, address))

# Kết nối và lưu trữ dữ liệu vào database MySQL
conn = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='123',
    database='foody_db'
)
cursor = conn.cursor()
for restaurant in restaurants:
    cursor.execute('INSERT INTO restaurants (name, address) VALUES (%s, %s)', restaurant)
conn.commit()
cursor.close()
conn.close()
