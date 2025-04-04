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

def find_restaurant(query):
    sql = """SELECT id, name
        FROM restaurants
        WHERE LOWER(name) LIKE LOWER(?)
        ORDER BY name DESC"""
    like = "%" + query + "%"
    return db.query(sql, [like])


def add_review(restaurant_id, user_id, rating, comment):
    sql = "INSERT INTO reviews (restaurant_id, user_id, rating, comment) VALUES (?, ?, ?, ?)"
    db.execute(sql, [restaurant_id, user_id, rating, comment])

def get_reviews(restaurant_id):
    sql = """SELECT r.id, r.user_id, r.rating, r.comment, r.created_at, u.username
             FROM reviews r
             JOIN users u ON r.user_id = u.id
             WHERE r.restaurant_id = ?
             ORDER BY r.created_at DESC"""
    return db.query(sql, [restaurant_id])

def get_review(review_id):
    sql = "SELECT id, restaurant_id, user_id, rating, comment FROM reviews WHERE id = ?"
    return db.query(sql, [review_id])[0]

def remove_review(review_id):
    sql = "DELETE FROM reviews WHERE id = ?"
    db.execute(sql, [review_id])

#def update_review(review_id, rating, comment):