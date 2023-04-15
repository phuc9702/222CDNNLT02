from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Response
from fastapi import status
from fastapi import Query
from pydantic import BaseModel
from typing import List
from fastapi.responses import HTMLResponse
import mysql.connector


app = FastAPI()

# Kết nối tới database
db = mysql.connector.connect(
    host="127.0.0.1",
    user="root",  # Thay thế bằng tên người dùng của bạn
    password="123456",  # Thay thế bằng mật khẩu của bạn
    database="foody_db"  # Thay thế bằng tên database của bạn
)
cursor = db.cursor()


# Model dùng để định nghĩa dữ liệu đầu vào cho API
class Restaurant(BaseModel):
    id: int
    name: str
    address: str
    city: str
    phone:str
    rating: float


# Route hiển thị trang chủ với search box
@app.get("/", response_class=HTMLResponse)
def home():
    html = """
        <html>
            <head>
                <title>Foody.vn</title>
            </head>
            <body>
                <h1>Search for restaurants</h1>
                <form action="/restaurants" method="get">
                    <input type="text" name="query" placeholder="Enter restaurant name...">
                    <input type="submit" value="Search">
                </form>
            </body>
        </html>
    """
    return html


# Route lấy danh sách nhà hàng dựa trên query từ search box
@app.get("/restaurants", response_model=List[Restaurant])
def search_restaurants(query: str = Query(...)):
    cursor.execute(f"SELECT * FROM restaurants WHERE name LIKE '%{query}%'")
    results = cursor.fetchall()
    if not results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No restaurants found")
    restaurants = []
    for row in results:
        restaurant = Restaurant(id=row[0], name=row[1], address=row[2], rating=row[3])
        restaurants.append(restaurant)
    return restaurants

# Route cập nhật thông tin của một nhà hàng
@app.put("/restaurants/{restaurant_id}", response_model=Restaurant)
def update_restaurant(restaurant_id: int, restaurant: Restaurant):
    cursor.execute(
        f"UPDATE restaurants SET name='{restaurant.name}', address='{restaurant.address}', rating={restaurant.rating} WHERE id={restaurant_id}"
    )
    db.commit()
    cursor.execute(f"SELECT * FROM restaurants WHERE id={restaurant_id}")
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
    updated_restaurant = Restaurant(id=row[0], name=row[1], address=row[2], rating=row[3])
    return updated_restaurant

@app.delete("/restaurants/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_restaurant(restaurant_id: int):
    cursor.execute(f"SELECT * FROM restaurants WHERE id={restaurant_id}")
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
        cursor.execute(f"DELETE FROM restaurants WHERE id={restaurant_id}")
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.on_event("shutdown")
def shutdown_event():
    cursor.close()
    db.close()