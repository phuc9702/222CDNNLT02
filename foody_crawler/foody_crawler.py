from fastapi import FastAPI
from pydantic import BaseModel
from bs4 import BeautifulSoup
import requests
import mysql.connector

# Định nghĩa mô hình dữ liệu cho món ăn
class Food(BaseModel):
    name: str
    description: str
    image_url: str

# Khởi tạo ứng dụng FastAPI
app = FastAPI()

# Thiết lập kết nối đến cơ sở dữ liệu MySQL
mydb = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="123456",
    database="foody_db"
)
mycursor = mydb.cursor()

# Tìm kiếm món ăn dựa trên tên
@app.get("Home/{food_name}")
async def search_food(food_name: str):
    query = "SELECT * FROM foods WHERE name LIKE %s"
    values = ('%' + food_name + '%',)
    mycursor.execute(query, values)
    result = mycursor.fetchall()
    foods = []
    for row in result:
        food = Food(name=row[1], description=row[2], image_url=row[3])
        foods.append(food)
    return {"message": f"Search results for food name '{food_name}'", "data": foods}

# Cào dữ liệu từ trang web foody.vn và lưu vào cơ sở dữ liệu MySQL
@app.get("/crawl")
async def crawl_foody():
    # Gửi yêu cầu GET đến trang web foody.vn
    response = requests.get("https://www.foody.vn/")
    soup = BeautifulSoup(response.content, 'html.parser')

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


# Cập nhật thông tin của một món ăn
@app.put("/foods/{food_id}")
async def update_food(food_id: int, food: Food):
    query = "UPDATE foods SET name = %s, description = %s, image_url = %s WHERE id = %s"
    values = (food.name, food.description, food.image_url, food_id)
    mycursor.execute(query, values)
    mydb.commit()
@app.put("/foods/{food_id}")
async def update_food(food_id: int, food: Food):
    query = "UPDATE foods SET name = %s, description = %s, image_url = %s WHERE id = %s"
    values = (food.name, food.description, food.image_url, food_id)
    mycursor.execute(query, values)
    mydb.commit()
    return {"message": f"Food with id {food_id} updated successfully"}

#Xóa một món ăn
@app.delete("/foods/{food_id}")
async def delete_food(food_id: int):
    query = "DELETE FROM foods WHERE id = %s"
    values = (food_id,)
    mycursor.execute(query, values)
    mydb.commit()
    return {"message": f"Food with id {food_id} deleted successfully"}
if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8000)

