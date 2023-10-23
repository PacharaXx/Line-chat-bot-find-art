#!/usr/bin/python

import sqlite3

conn = sqlite3.connect('test.db')
print ("Opened database successfully")

conn.execute('''CREATE TABLE Artworks (
    artwork_id INT PRIMARY KEY,
    title VARCHAR(255),
    artist VARCHAR(255),
    description TEXT,
    creation_date DATE
);''')
print ("Table created successfully")

conn.execute('''CREATE TABLE ArtworkColors (
    artwork_id INT,
    color_id INT,
    FOREIGN KEY (artwork_id) REFERENCES Artworks (artwork_id),
    FOREIGN KEY (color_id) REFERENCES Colors (color_id)
);''')
print ("Table created successfully")

conn.execute('''CREATE TABLE Colors (
    color_id INT PRIMARY KEY,
    color_name VARCHAR(50),
    color_description VARCHAR(255),
    color_hex CHAR(7)
);''')
print ("Table created successfully")

conn.execute('''CREATE TABLE Images (
    image_id INT PRIMARY KEY,
    image_url VARCHAR(255)
);''')
print ("Table created successfully")

conn.execute('''CREATE TABLE ArtworkImages (
    artwork_id INT,
    image_id INT,
    FOREIGN KEY (artwork_id) REFERENCES Artworks (artwork_id),
    FOREIGN KEY (image_id) REFERENCES Images (image_id)
);''')
print ("Table created successfully")

conn.close()