DROP TABLE IF EXISTS products;

CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    category TEXT NOT NULL,
    price_inr REAL NOT NULL,
    price_gbp REAL NOT NULL,
    description TEXT,
    length REAL,
    height REAL,
    width REAL,
    weight REAL,
    material TEXT,
    image1 TEXT,
    image2 TEXT,
    image3 TEXT,
    image4 TEXT,
    video TEXT,
    rating REAL DEFAULT 0,
    rating_count INTEGER DEFAULT 0
);
