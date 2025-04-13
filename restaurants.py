import db

def add_restaurant(name, address, link, user_id):
    sql = "INSERT INTO restaurants (name, address, link, user_id) VALUES (?, ?, ?, ?)"
    db.execute(sql, [name, address, link, user_id])

def get_restaurants():
    sql = """SELECT r.id, r.name, r.address, r.link, user_id
             FROM restaurants r
             GROUP BY r.id
             ORDER BY r.name"""
    return db.query(sql)

def get_restaurant(restaurant_id):
    sql = "SELECT id, name, address, link, user_id FROM restaurants WHERE id = ?"
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

def update_review(review_id, rating, comment):
    sql = "UPDATE reviews SET rating = ?, comment = ? WHERE id = ?"
    db.execute(sql, [rating, comment, review_id])

def create_tag(user_id, tag_name):
    sql = "INSERT INTO tags (user_id, name) VALUES (?, ?)"
    db.execute(sql, [user_id, tag_name])

def get_tags():
    sql = "SELECT id, name FROM tags ORDER BY name"
    return db.query(sql)

def get_restaurant_tags(restaurant_id):
    sql = """SELECT t.id, t.name
             FROM tags t
             JOIN restaurant_tags rt ON t.id = rt.tag_id
             WHERE rt.restaurant_id = ?
             ORDER BY t.name"""
    return db.query(sql, [restaurant_id])

def associate_tag_with_restaurant(restaurant_id, tag_id):
    sql = "INSERT INTO restaurant_tags (restaurant_id, tag_id) VALUES (?, ?)"
    db.execute(sql, [restaurant_id, tag_id])

def remove_tag_from_restaurant(restaurant_id, tag_id):
    sql = "DELETE FROM restaurant_tags WHERE restaurant_id = ? AND tag_id = ?"
    db.execute(sql, [restaurant_id, tag_id])
