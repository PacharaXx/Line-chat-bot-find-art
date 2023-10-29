import sqlite3

# สร้างเชื่อมต่อกับฐานข้อมูล
conn = sqlite3.connect("test.db")
cursor = conn.cursor()

# สร้างตาราง Artworks
cursor.execute(
    """
    CREATE TABLE Artworks (
        artwork_id INT PRIMARY KEY,
        title VARCHAR(255),
        artist VARCHAR(255),
        description TEXT,
        creation_date DATE,
        image_url VARCHAR(255)
    );
"""
)

# สร้างตาราง Colors
cursor.execute(
    """
    CREATE TABLE Colors (
        color_id INT PRIMARY KEY,
        color_name VARCHAR(50)
    );
"""
)

# สร้างตาราง ArtworkColors
cursor.execute(
    """
    CREATE TABLE ArtworkColors (
        artwork_color_id INT PRIMARY KEY,
        artwork_id INT,
        color_id INT,
        FOREIGN KEY (artwork_id) REFERENCES Artworks(artwork_id),
        FOREIGN KEY (color_id) REFERENCES Colors(color_id)
    );
"""
)

# เพิ่มคอลัมน์ "color_name" ในตาราง "ArtworkColors"
cursor.execute(
    """
    ALTER TABLE ArtworkColors
    ADD COLUMN color_name VARCHAR(50);
"""
)

artworks = [
    {
        # "artworks_id": len(artworks) + 1,
        "artworks_id": 1,
        "title": "Title A",
        "artist": "Artist A",
        "description": "Description A",
        "creation_date": "2023-10-25",
        "image_url": "image1.jpg",
    },
    {
        "artworks_id": 2,
        "title": "Title B",
        "artist": "Artist B",
        "description": "Description B",
        "creation_date": "2023-10-27",
        "image_url": "image2.jpg",
    },
]
# artworks.append()

# เพิ่มข้อมูลตัวอย่างในตาราง "Artworks"
for art in artworks:
    cursor.execute(
        "INSERT INTO Artworks (artwork_id, title, artist, description, creation_date, image_url) VALUES (?, ?, ?, ?, ?, ?)",
        (
            art["artworks_id"],
            art["title"],
            art["artist"],
            art["description"],
            art["creation_date"],
            art["image_url"],
        ),
    )

color_names = {
    (0, 0, 255): ("Blue", 1),
    (255, 0, 0): ("Red", 2),
    (255, 255, 0): ("Yellow", 3),
    (128, 0, 128): ("Violet", 4),
    (255, 165, 0): ("Orange", 5),
    (0, 128, 0): ("Green", 6),
    (138, 43, 226): ("Blue-Violet", 7),
    (255, 69, 0): ("Red-Orange", 8),
    (255, 215, 0): ("Yellow-Orange", 9),
    (0, 128, 128): ("Blue-Green", 10),
    (128, 0, 0): ("Red-Violet", 11),
    (173, 255, 47): ("Yellow-Green", 12),
    (0, 0, 0): ("Black", 13),
    (255, 255, 255): ("White", 14),
}
for rgb, (color_name, color_id) in color_names.items():
    cursor.execute(
        "INSERT INTO Colors (color_id, color_name) VALUES (?, ?)",
        (color_id, color_name),
    )

# เพิ่มข้อมูลตัวอย่างในตาราง "ArtworkColors"
# if have artwork_id in Artwork insert artwork_id to ArtworkColors and artwork_color_id = len of row + 1
cursor.execute(
    "INSERT INTO ArtworkColors (artwork_color_id, artwork_id, color_id, color_name) VALUES ((SELECT COUNT(*) + 1 FROM ArtworkColors), 1, NULL, NULL)"
)

# อัปเดตคอลัมน์ "color_name" จากตาราง "Colors"
cursor.execute(
    """
    UPDATE ArtworkColors
    SET color_name = (
        SELECT color_name
        FROM Colors
        WHERE Colors.color_id = ArtworkColors.color_id
    );
"""
)

# ยืนยันการเพิ่มข้อมูล
conn.commit()

# ปิดเชื่อมต่อกับฐานข้อมูล
conn.close()
