from fastapi import FastAPI
from pydantic import BaseModel
from tortoise import Tortoise, fields
from tortoise.models import Model
from tortoise.contrib.fastapi import register_tortoise
from tortoise.transactions import in_transaction
import requests
from bs4 import BeautifulSoup

app = FastAPI()

class FoodItem(BaseModel):
    name: str
    price: str
    rating: float

class Food(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    price = fields.CharField(max_length=255)
    rating = fields.FloatField()

async def get_html(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

async def parse_food_items(html):
    soup = BeautifulSoup(html, 'html.parser')
    food_items = []
    for item in soup.find_all('div', class_='food-item'):
        name = item.find('h4', class_='food-name').text.strip()
        price = item.find('p', class_='food-price').text.strip()
        rating = float(item.find('span', class_='food-rating').text.strip())
        food_item = FoodItem(name=name, price=price, rating=rating)
        food_items.append(food_item)
    return food_items

async def crawl_data():
    url = 'https://www.foody.vn/da-nang'
    html = await get_html(url)
    food_items = await parse_food_items(html)
    async with in_transaction() as conn:
        for food_item in food_items:
            food = Food(name=food_item.name, price=food_item.price, rating=food_item.rating)
            await food.save()

@app.on_event('startup')
async def startup_event():
    await Tortoise.init(db_url='mysql://root:123456@127.0.0.1/foody_db')
    await Tortoise.generate_schemas()
    await crawl_data()

@app.on_event('shutdown')
async def shutdown_event():
    await Tortoise.close_connections()

@app.get('/')
async def read_home():
    return {'message': 'Welcome to Foody API!'}

@app.get('/foods', response_model=list[Food])
async def get_foods():
    foods = await Food.all()
    return foods

@app.post('/foods', response_model=Food)
async def create_food(food: Food):
    food = Food(name=food.name, price=food.price, rating=food.rating)
    await food.save()
    return food

@app.put('/foods/{food_id}', response_model=Food)
async def update_food(food_id: int, food: Food):
    await Food.filter(id=food_id).update(name=food.name, price=food.price, rating=food.rating)
    updated_food = await Food.get(id=food_id)
    return updated_food

@app.delete('/foods/{food_id}', response_model=dict)
async def delete_food(food_id: int):
    deleted_count = await Food.filter(id=food_id).delete()
    return {'deleted_count': deleted_count}
