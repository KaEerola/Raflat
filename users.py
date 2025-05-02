import db

def get_user(username):
    sql = "SELECT id, username, created_at FROM users WHERE username = ?"
    result = db.query(sql, [username])
    return result[0] if result else None

def get_user_reviews(user_id, page, page_size):
    sql = """SELECT r.id, r.user_id, r.restaurant_id, r.rating, r.comment, r.created_at, u.username, re.name AS restaurant_name
             FROM reviews r
             JOIN users u ON r.user_id = u.id
             JOIN restaurants re ON r.restaurant_id = re.id
             WHERE u.id = ?
             ORDER BY r.created_at DESC
             LIMIT ? OFFSET ?"""
    limit = page_size
    offset = (page - 1) * page_size
    result = db.query(sql, [user_id, limit, offset])
    return result if result else None

def count_reviews_by_user(user_id):
    sql = "SELECT COUNT(*) AS count FROM reviews WHERE user_id = ?"
    return db.query(sql, [user_id])[0]["count"]

def get_user_restaurants(user_id, page, page_size):
    sql = """SELECT re.id, re.name, re.address, re.link
             FROM restaurants re
             JOIN users u ON re.user_id = u.id
             WHERE u.id = ?
             GROUP BY re.id
             ORDER BY re.name
             LIMIT ? OFFSET ?"""
    limit = page_size
    offset = (page - 1) * page_size
    result = db.query(sql, [user_id, limit, offset])
    return result if result else None

def count_restaurants_by_user(user_id):
    sql = "SELECT COUNT(*) AS count FROM restaurants WHERE user_id = ?"
    return db.query(sql, [user_id])[0]["count"]

def get_user_tags(user_id):
    sql = """SELECT t.id, t.user_id, t.name
             FROM tags t
             JOIN users u ON t.user_id = u.id
             WHERE u.id = ?
             GROUP BY t.id
             ORDER BY t.name"""
    result = db.query(sql, [user_id])
    return result if result else None

def find_users(query, page, page_size):
    sql = """SELECT id, username
             FROM users
             WHERE LOWER(username) LIKE LOWER(?)
             ORDER BY username ASC
             LIMIT ? OFFSET ?"""
    limit = page_size
    offset = offset = (page - 1) * page_size
    like = "%" + query + "%"
    return db.query(sql, [like, limit, offset])

def count_user_matches(query):
    sql = """SELECT COUNT(*) AS count
             FROM users
             WHERE LOWER(username) LIKE LOWER(?)"""
    like = "%" + query + "%"
    return db.query(sql, [like])[0]["count"]