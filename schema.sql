CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS restaurants (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    address TEXT,
    user_id INTEGER REFERENCES users,
    link TEXT
);

CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY,
    restaurant_id INTEGER REFERENCES restaurants,
    user_id INTEGER REFERENCES users,
    rating INTEGER NOT NULL,
    comment TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users,
    name TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS restaurant_Tags (
    restaurant_id INTEGER REFERENCES restaurants,
    tag_id INTEGER REFERENCES tags,
    PRIMARY KEY (restaurant_id, tag_id)
);

-- Index on restaurant_id in the reviews table
CREATE INDEX IF NOT EXISTS idx_reviews_restaurant_id ON reviews (restaurant_id);

-- Index on user_id in the reviews table
CREATE INDEX IF NOT EXISTS idx_reviews_user_id ON reviews (user_id);