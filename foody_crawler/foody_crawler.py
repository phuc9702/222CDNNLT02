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
    def __init__(self, name, address):
        self.name = name
        self.address = address
  

# Hàm cào dữ liệu từ trang web và lưu vào cơ sở dữ liệu MySQL
@app.get("/crawl")
async def crawl_foody():
    # Gửi yêu cầu GET đến trang web foody.vn
    response = requests.get("https://www.foody.vn/da-nang")
    soup = BeautifulSoup(response.content, 'html.parser')

    # Xóa dữ liệu cũ trong cơ sở dữ liệu
    query = "DELETE FROM foods"
    mycursor.execute(query)
    mydb.commit()

    # Tìm kiếm các phần tử HTML chứa thông tin về món ăn
    foods = []
    for food_item in soup.find_all("li", class_="item in ListItem.items"):
        name = food_item.find("div", class_="name limit-text").text.strip()
        address = food_item.find("div", class_="address limit-text").text.strip()
        food = Food(name=name, address=address )
        foods.append(food)

        # Lưu thông tin vào cơ sở dữ liệu MySQL
        query = "INSERT INTO foods (name, address, ) VALUES (%s, %s)"
        values = (food.name, food.description)
        mycursor.execute(query, values)
        mydb.commit()

    return {"message": "Data crawled and saved successfully", "data": foods}

# Hàm tìm kiếm dữ liệu theo từ khóa trên trang chủ
@app.get("/")
async def search_foody(keyword: str):
    # Tìm kiếm dữ liệu trong cơ sở dữ liệu MySQL
    query = "SELECT * FROM foods WHERE name LIKE %s OR address LIKE %s"
    values = ("%" + keyword + "%", "%" + keyword + "%")
    mycursor.execute(query, values)
    result = mycursor.fetchall()

    # Chuyển kết quả thành đối tượng Food và trả về dữ liệu dưới dạng JSON
    foods = []
    for item in result:
        food = Food(name=item[1], address=item[2])
        foods.append(food)
#Tiếp tục hàm tìm kiếm dữ liệu theo từ khóa trên trang chủ
    return {"message": "Search result for keyword: {}".format(keyword), "data": foods}

if __name__ == "__main__":
# Chạy ứng dụng FastAPI bằng giao thức Uvicorn trên cổng 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)