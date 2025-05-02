import db

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

def get_tag_by_id(tag_id):
    sql = "SELECT * FROM tags WHERE id = ?"
    result = db.query(sql, [tag_id])
    return result[0] if result else None

def remove_tag_associations(tag_id):
    sql = "DELETE FROM restaurant_tags WHERE tag_id = ?"
    db.execute(sql, [tag_id])

def delete_tag(tag_id):
    sql = "DELETE FROM tags WHERE id = ?"
    db.execute(sql, [tag_id])