import mysql.connector

# Thiết lập thông tin kết nối
mydb = mysql.connector.connect(
  host="127.0.0.1",
  user="root",
  password="123",
  database="foody_db"
)

# Tạo đối tượng cursor để thực hiện các thao tác trên cơ sở dữ liệu
cursor = mydb.cursor()

# INSERT: Thêm dữ liệu mới vào bảng
sql = "INSERT INTO restaurant (name, address) VALUES (%s, %s)"
val = ("Restaurant Name", "Restaurant Address")
cursor.execute(sql, val)
mydb.commit()
print("Đã thêm dữ liệu vào cơ sở dữ liệu")

# SELECT: Truy vấn dữ liệu từ bảng
sql = "SELECT * FROM restaurant"
cursor.execute(sql)
results = cursor.fetchall()
for row in results:
    print(row)

# UPDATE: Cập nhật dữ liệu trong bảng
sql = "UPDATE restaurant SET name = %s WHERE id = %s"
val = ("New Restaurant Name", 1)
cursor.execute(sql, val)
mydb.commit()
print("Đã cập nhật dữ liệu trong cơ sở dữ liệu")

# DELETE: Xóa dữ liệu từ bảng
sql = "DELETE FROM restaurant WHERE id = %s"
val = (1,)
cursor.execute(sql, val)
mydb.commit()
print("Đã xóa dữ liệu từ cơ sở dữ liệu")

# Đóng kết nối
cursor.close()
mydb.close()
