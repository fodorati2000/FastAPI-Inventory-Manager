from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from databse import Database_Manager
import os
import shutil

app = FastAPI()
from fastapi.staticfiles import StaticFiles

upload_dir = "static/images"
if not os.path.exists(upload_dir):
    os.makedirs(upload_dir)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_m = Database_Manager()
db_m.create_table()

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    res = db_m.login(username, password) 
    
    if res.get("status") == "Success":
        return {"status": "Success", "message": "Bent vagy!"}
    else:
        return {"status": "Error", "message": res.get("message", "Hiba")}
    

@app.post("/register")
async def register(username: str = Form(...), password: str = Form(...)):
    res = db_m.register(username, password) 

    if res.get("status") == "Success":
        return {"status": "Success", "message": "Sikeres regisztráció!"}
    else:
        return {"status": "Error", "message": res.get("message", "Hiba")}



@app.post("/brands/new")
def add_brand(name: str = Form(...)):
    return db_m.add_values("brands", name)

@app.post("/categories/new")
def add_category(name: str = Form(...)):
    return db_m.add_values("categories", name)

@app.post("/locations/new")
def add_location(name: str = Form(...)):
    return db_m.add_values("locations", name)

@app.post("/products/new")
async def add_product(
    name: str = Form(...),
    brand_id: int = Form(...),
    category_id: int = Form(...),
    location_id: int = Form(...),
    purchase_price: int = Form(...),
    sale_price: int = Form(...),
    stock_quantity: int = Form(...),
    condition: str = Form(...),
    file: UploadFile = File(...)
):
    filename = f"{name}_{file.filename}".replace(" ", "_")
    file_path = os.path.join(upload_dir, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return db_m.add_product(
        name, brand_id, category_id, location_id, 
        purchase_price, sale_price, stock_quantity, 
        condition, filename
    )

@app.get("/list")
def list_products():
    return db_m.get_all_product()

@app.delete("/delete/{product_id}")
def delete_product(product_id: int):
    db_m.delete_product(product_id)
    return {"status": "deleted"}

@app.put("/edit")
def edit_product(
    product_id: int = Form(...),
    name: str = Form(...),
    brand_id: int = Form(...), # Név helyett ID
    category_id: int = Form(...), # Név helyett ID
    location_id: int = Form(...), # Név helyett ID
    purchase_price: int = Form(...),
    sale_price: int = Form(...),
    stock_quantity: int = Form(...),
    condition: str = Form(...)
):  
    return db_m.edit_product(
        product_id, name, brand_id, category_id, 
        location_id, purchase_price, sale_price, 
        stock_quantity, condition
    )

@app.get("/brands")
def get_brands():
    return db_m.get_brands()

@app.get("/categories")
def get_categories():
    return db_m.get_categories()

@app.get("/locations")
def get_locations():
    return db_m.get_locations()

@app.get("/low-stock")
def get_low_stock():
    return db_m.get_low_stock()