import db

def get_user(user_id):
    sql = "SELECT id, username FROM users WHERE user_id = ?"
    result = db.query(sql, [user_id])
    return result[0][0] if result else None