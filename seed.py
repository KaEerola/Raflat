import random
import sqlite3

# Connect to the database
db = sqlite3.connect("database.db")

# Clear existing data from the tables
db.execute("DELETE FROM restaurant_Tags")
db.execute("DELETE FROM reviews")
db.execute("DELETE FROM restaurants")
db.execute("DELETE FROM tags")
db.execute("DELETE FROM users")

# Counts for generating data
user_count = 1000
restaurant_count = 10**5  # Number of restaurants
tag_count = 20  # Number of tags
review_count = 10**6  # Number of reviews for random restaurants

# Insert users
for i in range(1, user_count + 1):
    db.execute("INSERT INTO users (username) VALUES (?)", ["user" + str(i)])

# Insert restaurants
for i in range(1, restaurant_count + 1):
    db.execute("INSERT INTO restaurants (name, address, user_id, link) VALUES (?, ?, ?, ?)",
               [f"Restaurant {i}", f"Address {i}", random.randint(1, user_count), f"http://restaurant{i}.com"])

# Insert tags
for i in range(1, tag_count + 1):
    db.execute("INSERT INTO tags (user_id, name) VALUES (?, ?)",
               [random.randint(1, user_count), f"tag{i}"])

# Insert restaurant_tags (random associations between restaurants and tags)
for i in range(1, restaurant_count + 1):
    num_tags = random.randint(1, 5)  # Each restaurant gets 1 to 5 tags
    tags = random.sample(range(1, tag_count + 1), num_tags)  # Select random tags
    for tag_id in tags:
        db.execute("INSERT INTO restaurant_Tags (restaurant_id, tag_id) VALUES (?, ?)", [i, tag_id])

# Insert reviews (random reviews for restaurants)
for i in range(1, review_count + 1):
    restaurant_id = random.randint(1, restaurant_count)
    user_id = random.randint(1, user_count)
    rating = random.randint(1, 5)  # Rating between 1 and 5
    db.execute("""INSERT INTO reviews (restaurant_id, user_id, rating, comment, created_at)
                  VALUES (?, ?, ?, ?, datetime('now'))""",
               [restaurant_id, user_id, rating, f"Review comment {i}"])

# Commit and close the database
db.commit()
db.close()
