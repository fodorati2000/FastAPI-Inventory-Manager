from fastapi import HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import bcrypt

class Database_Manager:
    def __init__(self):
        self.host = "db"
        self.user = "admin"
        self.password = "titkosjelszo"
        self.dbname = "raktar_bolt"

    def get_connection(self):
        return psycopg2.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            dbname=self.dbname,
            cursor_factory=RealDictCursor
        )

    def create_table(self):
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("CREATE TABLE IF NOT EXISTS brands (id SERIAL PRIMARY KEY, name TEXT UNIQUE NOT NULL)")
                cursor.execute("CREATE TABLE IF NOT EXISTS categories (id SERIAL PRIMARY KEY, name TEXT UNIQUE NOT NULL)")
                cursor.execute("CREATE TABLE IF NOT EXISTS locations (id SERIAL PRIMARY KEY, name TEXT UNIQUE NOT NULL)")
                cursor.execute("""
                                CREATE TABLE IF NOT EXISTS users (
                                    id SERIAL PRIMARY KEY,
                                    username VARCHAR(50) UNIQUE NOT NULL,
                                    password VARCHAR(255) NOT NULL   
                                )
                            """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS products (
                        id SERIAL PRIMARY KEY,
                        name TEXT NOT NULL,
                        brand_id INTEGER REFERENCES brands(id),
                        category_id INTEGER REFERENCES categories(id),
                        location_id INTEGER REFERENCES locations(id),
                        purchase_price INTEGER DEFAULT 0,
                        sale_price INTEGER DEFAULT 0,
                        stock_quantity INTEGER DEFAULT 0,
                        condition TEXT,
                        image_path TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
        except Exception as e:
            print(f"Error: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def login(self, username, password):
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                # 1. Lekérjük a nevet és a jelszót (hash-t)
                query = "SELECT username, password FROM users WHERE username = %s"
                cursor.execute(query, (username,))
                result = cursor.fetchone()
                
                if result:
                    db_username = result['username']
                    stored_hash = result['password'] # Ez az adatbázisból jövő hash

                    # BIZTONSÁGI JAVÍTÁS: 
                    # A bcryptnek bytes kell. Ha stringet kaptunk, kódoljuk át.
                    if isinstance(stored_hash, str):
                        stored_hash = stored_hash.encode('utf-8')
                    
                    # A beírt jelszót is bytes-szá alakítjuk
                    typed_password_bytes = password.encode('utf-8')

                    # 2. Ellenőrzés
                    if bcrypt.checkpw(typed_password_bytes, stored_hash):
                        return {"status": "Success", "username": db_username}
                
                # Ha nincs találat vagy nem egyezik a jelszó
                return {"status": "Error", "message": "Hibás név vagy jelszó"}

        except Exception as e:
            # Itt kiíratjuk a pontos hibát a logba, hogy ne csak egy '0'-át lássunk
            import traceback
            print("PONTOS HIBA ÜZENET:")
            print(traceback.format_exc()) 
            return {"status": "Error", "message": "Szerver hiba történt"}
        finally:
            conn.close()

    def register(self, username, pw):
        conn = self.get_connection()
        try:
            if not username or not pw:
                return {"status": "Error", "message": "Minden mezőt ki kell tölteni!"}
            
            password_bytes = pw.encode('utf-8')
            salt = bcrypt.gensalt()
            hashed_password_bytes = bcrypt.hashpw(password_bytes, salt)

            # Ez a fontos lépés: alakítsd bytes-ból stringgé!
            hashed_password_string = hashed_password_bytes.decode('utf-8')

            with conn.cursor() as cursor:
                query = "INSERT INTO users (username, password) VALUES (%s, %s)"
                
                cursor.execute(query, (username, hashed_password_string))
                

                conn.commit()
                return {"status": "Success", "username": username}
        except Exception as e:
            conn.rollback()
            return {"status": "Error", "message": str(e)}
        finally:
            conn.close()


    def add_values(self, table_name, name):
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                query = f"INSERT INTO {table_name} (name) VALUES (%s)"
                cursor.execute(query, (name,))
                conn.commit()
                return {"status": "Success"}
        finally:
            conn.close()
        
    def add_product(self, name, brand_id, category_id, location_id, p_price, s_price, stock, condition, filename):
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO products (name, brand_id, category_id, location_id, purchase_price, sale_price, stock_quantity, condition, image_path)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (name, brand_id, category_id, location_id, p_price, s_price, stock, condition, filename))
                conn.commit()
                return {"status": "Product saved"}
        finally:
            conn.close()
    
    def get_all_product(self):
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT p.id, p.name, p.image_path, p.purchase_price, p.sale_price, p.stock_quantity, p.condition,
                           b.name AS brand_name, c.name AS category_name, l.name AS location_name
                    FROM products p
                    LEFT JOIN brands b ON p.brand_id = b.id
                    LEFT JOIN categories c ON p.category_id = c.id
                    LEFT JOIN locations l ON p.location_id = l.id
                """)
                return cursor.fetchall()
        finally:
            conn.close()
        
    def delete_product(self, product_id):
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
                conn.commit()
        finally:
            conn.close()

    def edit_product(self, product_id, name, brand_id, category_id, location_id, p_price, s_price, stock, condition):
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
               
                
                cursor.execute("""
                    UPDATE products 
                    SET name = %s, 
                        brand_id = %s, 
                        category_id = %s, 
                        location_id = %s, 
                        purchase_price = %s, 
                        sale_price = %s, 
                        stock_quantity = %s, 
                        condition = %s
                    WHERE id = %s
                """, (
                    name, 
                    brand_id, 
                    category_id, 
                    location_id, 
                    p_price, 
                    s_price, 
                    stock, 
                    condition, 
                    product_id
                ))
                conn.commit()
        except Exception as e:
            print(f"Database error: {e}")
            raise e
        finally:
            conn.close()

    def get_brands(self):
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT id, name FROM brands")
                return cursor.fetchall() 
        finally:
            conn.close()

    def get_categories(self):
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT id, name FROM categories")
                return cursor.fetchall()
        finally:
            conn.close()

    def get_locations(self):
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT id, name FROM locations")
                return cursor.fetchall()
        finally:
            conn.close()

    def get_low_stock(self):
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT p.id, p.name, p.image_path, p.purchase_price, p.sale_price, p.stock_quantity, p.condition,
                           b.name AS brand_name, c.name AS category_name, l.name AS location_name
                    FROM products p
                    LEFT JOIN brands b ON p.brand_id = b.id
                    LEFT JOIN categories c ON p.category_id = c.id
                    LEFT JOIN locations l ON p.location_id = l.id
                    WHERE p.stock_quantity < 5
                    """) 
                return cursor.fetchall()
        finally:
            conn.close()