import db

def get_user(username):
    sql = "SELECT id, username, created_at FROM users WHERE username = ?"
    result = db.query(sql, [username])
    return result[0] if result else None

def get_user_reviews(user_id):
    sql = """SELECT r.id, r.restaurant_id, r.rating, r.comment, r.created_at, u.username, re.name AS restaurant_name
             FROM reviews r
             JOIN users u ON r.user_id = u.id
             join restaurants re ON r.restaurant_id = re.id
             WHERE u.id = ?
             ORDER BY r.created_at DESC"""
    result = db.query(sql, [user_id])
    return result if result else None

def get_user_restaurants(user_id):
    sql = """SELECT re.id, re.name, re.address, re.link
             FROM restaurants re
             JOIN users u ON re.user_id = u.id
             WHERE u.id = ?
             GROUP BY re.id
             ORDER BY re.name"""
    result = db.query(sql, [user_id])
    return result if result else None

def get_user_tags(user_id):
    sql = """SELECT t.id, t.name
             FROM tags t
             JOIN users u ON t.user_id = u.id
             WHERE u.id = ?
             GROUP BY t.id
             ORDER BY t.name"""
    result = db.query(sql, [user_id])
    return result if result else None