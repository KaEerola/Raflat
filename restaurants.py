import db

def add_restaurant(name, address, link, user_id):
    sql = "INSERT INTO restaurants (name, address, link, user_id) VALUES (?, ?, ?, ?)"
    db.execute(sql, [name, address, link, user_id])

def get_restaurants(page, page_size):
    sql = """SELECT r.id, r.name, r.address, r.link, r.user_id
             FROM restaurants r
             GROUP BY r.id
             ORDER BY r.name
             LIMIT ? OFFSET ?"""
    limit = page_size
    offset = (page - 1) * page_size
    return db.query(sql, [limit, offset])

def get_restaurant_count():
    sql = "SELECT COUNT(*) FROM restaurants"
    result = db.query(sql)
    return result[0][0] if result else 0

def get_restaurant(restaurant_id):
    sql = "SELECT id, name, address, link, user_id FROM restaurants WHERE id = ?"
    return db.query(sql, [restaurant_id])[0]

def update_restaurant(restaurant_id, name, address, link):
    sql = "UPDATE restaurants SET name = ?, address = ?, link = ? WHERE id = ?"
    db.execute(sql, [name, address, link, restaurant_id])

def remove_restaurant(restaurant_id):
    sql = "DELETE FROM restaurants WHERE id = ?"
    db.execute(sql, [restaurant_id])

def find_restaurant(query, page, page_size):
    sql = """SELECT DISTINCT r.id, r.name
             FROM restaurants r
             LEFT JOIN restaurant_tags rt ON r.id = rt.restaurant_id
             LEFT JOIN tags t ON rt.tag_id = t.id
             WHERE LOWER(r.name) LIKE LOWER(?) OR LOWER(t.name) LIKE LOWER(?)
             ORDER BY r.name DESC
             LIMIT ? OFFSET ?"""
    like = "%" + query + "%"
    limit = page_size
    offset = (page - 1) * page_size
    return db.query(sql, [like, like, limit, offset])

def count_restaurant_matches(query):
    sql = """SELECT COUNT(DISTINCT r.id) AS count
             FROM restaurants r
             LEFT JOIN restaurant_tags rt ON r.id = rt.restaurant_id
             LEFT JOIN tags t ON rt.tag_id = t.id
             WHERE LOWER(r.name) LIKE LOWER(?) OR LOWER(t.name) LIKE LOWER(?)"""
    like = "%" + query + "%"
    return db.query(sql, [like, like])[0]["count"]


def add_review(restaurant_id, user_id, rating, comment):
    sql = "INSERT INTO reviews (restaurant_id, user_id, rating, comment) VALUES (?, ?, ?, ?)"
    db.execute(sql, [restaurant_id, user_id, rating, comment])

def get_reviews(restaurant_id, sort = "newest", limit = 5, offset = 0):
    order_by = {
        "newest": "created_at DESC",
        "oldest": "created_at ASC",
        "highest": "rating DESC",
        "lowest": "rating ASC"
        }.get(sort, "created_at DESC")
    sql = f"""SELECT * FROM reviews
              WHERE restaurant_id = ?
              ORDER BY {order_by}
              LIMIT ? OFFSET ?"""
    return db.query(sql, [restaurant_id, limit, offset])

def count_reviews(restaurant_id):
    sql = "SELECT COUNT(*) AS count FROM reviews WHERE restaurant_id = ?"
    return db.query(sql, [restaurant_id])[0]["count"]

def get_review(review_id):
    sql = "SELECT id, restaurant_id, user_id, rating, comment FROM reviews WHERE id = ?"
    return db.query(sql, [review_id])[0]

def remove_review(review_id):
    sql = "DELETE FROM reviews WHERE id = ?"
    db.execute(sql, [review_id])

def update_review(review_id, rating, comment):
    sql = "UPDATE reviews SET rating = ?, comment = ? WHERE id = ?"
    db.execute(sql, [rating, comment, review_id])

def get_average_rating(restaurant_id):
    sql = """SELECT AVG(rating) AS average_rating
             FROM reviews
             WHERE restaurant_id = ?"""
    result = db.query(sql, [restaurant_id])
    return result[0][0] if result else None
