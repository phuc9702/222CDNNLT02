from bs4 import BeautifulSoup
import requests
import mysql.connector
from mysql.connector import Error
from fastapi import FastAPI
import uvicorn
import pymysql

# Khởi tạo ứng dụng FastAPI
app = FastAPI()

# Kết nối tới cơ sở dữ liệu MySQL
# Thiết lập kết nối
# Thiết lập kết nối
mydb = pymysql.connect(
  host="127.0.0.1",
  user="root",
  password="123456",
  database="foody_db"
)

# Tạo đối tượng cursor
mycursor = mydb.cursor()

# Thực hiện các thao tác CRUD
# Ví dụ: Thực hiện lệnh SELECT
mycursor.execute("SELECT * FROM foods")
results = mycursor.fetchall()
for row in results:
  print(row)
# Khai báo model cho đối tượng Food
class Food:
    def __init__(self, name, description, image_url):
        self.name = name
        self.description = description
        self.image_url = image_url

# Hàm cào dữ liệu từ trang web và lưu vào cơ sở dữ liệu MySQL
@app.get("/crawl")
async def crawl_foody():
    # Gửi yêu cầu GET đến trang web foody.vn
    response = requests.get("https://www.foody.vn/")
    soup = BeautifulSoup(response.content, 'html.parser')

    # Xóa dữ liệu cũ trong cơ sở dữ liệu
    query = "DELETE FROM foods"
    mycursor.execute(query)
    mydb.commit()

    # Tìm kiếm các phần tử HTML chứa thông tin về món ăn
    foods = []
    for food_item in soup.find_all("div", class_="row-item"):
        name = food_item.find("h2", class_="title").text.strip()
        description = food_item.find("p", class_="address").text.strip()
        image_url = food_item.find("img")["src"]
        food = Food(name=name, description=description, image_url=image_url)
        foods.append(food)

        # Lưu thông tin vào cơ sở dữ liệu MySQL
        query = "INSERT INTO foods (name, description, image_url) VALUES (%s, %s, %s)"
        values = (food.name, food.description, food.image_url)
        mycursor.execute(query, values)
        mydb.commit()

    return {"message": "Data crawled and saved successfully", "data": foods}

# Hàm tìm kiếm dữ liệu theo từ khóa trên trang chủ
@app.get("/")
async def search_foody(keyword: str):
    # Tìm kiếm dữ liệu trong cơ sở dữ liệu MySQL
    query = "SELECT * FROM foods WHERE name LIKE %s OR description LIKE %s"
    values = ("%" + keyword + "%", "%" + keyword + "%")
    mycursor.execute(query, values)
    result = mycursor.fetchall()

    # Chuyển kết quả thành đối tượng Food và trả về dữ liệu dưới dạng JSON
    foods = []
    for item in result:
        food = Food(name=item[1], description=item[2], image_url=item[3])
        foods.append(food)
        return {"message": "Search results", "data": foods}

if __name__ == "main":
    uvicorn.run(app, host="localhost", port=8000)