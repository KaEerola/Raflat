import db

def add_restaurant(name, address, link):
    sql = "INSERT INTO restaurants (name, address, link) VALUES (?, ?, ?)"
    db.execute(sql, [name, address, link])
    
def get_restaurants():
    sql = """SELECT r.id, r.name, r.address, r.link
             FROM restaurants r
             GROUP BY r.id
             ORDER BY r.name"""
    return db.query(sql)

def get_restaurant(restaurant_id):
    sql = "SELECT id, name, address, link FROM restaurants WHERE id = ?"
    return db.query(sql, [restaurant_id])[0]

def update_restaurant(restaurant_id, name, address, link):
    sql = "UPDATE restaurants SET name = ?, address = ?, link = ? WHERE id = ?"
    db.execute(sql, [name, address, link, restaurant_id])

def remove_restaurant(restaurant_id):
    sql = "DELETE FROM restaurants WHERE id = ?"
    db.execute(sql, [restaurant_id])