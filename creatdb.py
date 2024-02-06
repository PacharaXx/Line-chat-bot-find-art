import sqlite3

# สร้างเชื่อมต่อกับฐานข้อมูล
conn = sqlite3.connect("test1.db")
cursor = conn.cursor()


#  artwork_name = i['Artwork_Name']
#         artist_name = i['Artist_Name']
#         artwork_type = i['Artwork_Type']
#         artwork_size = i['Artwork_Size']
#         artwork_technique = i['Artwork_Technique']
#         exhibition_name = i['Exhibition_Name']
#         award_name = i['Award_Name']
#         license = i['License']
#         concept = i['Concept']
#         detail = i['Detail']
#         image_url = i['Image']
#         url = i['URL']
# สร้างตาราง Artworks
cursor.execute(
    """
    CREATE TABLE Artworks (
        artwork_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        artwork_name VARCHAR(255),
        artist_name VARCHAR(255),
        artwork_type VARCHAR(255),
        artwork_size VARCHAR(255),
        artwork_technique VARCHAR(255),
        exhibition_name VARCHAR(255),
        award_name VARCHAR(255),
        license VARCHAR(255),
        concept TEXT,
        detail TEXT,
        image_url VARCHAR(255),
        url VARCHAR(255)
    );
"""
)

# สร้างตาราง ArtworkEncodeds
cursor.execute(
    """
    CREATE TABLE ArtworkEncodeds (
        artwork_encoded_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        artwork_id INT UNIQUE,
        encoded BLOB,
        FOREIGN KEY (artwork_id) REFERENCES Artworks(artwork_id)
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
        "artwork_name": "\"ร่างกายแม่\" (แม่) หมายเลข 2",
        "artist_name": "อัฐพร นิมมาลัยแก้ว",
        "artwork_type": "จิตรกรรม",
        "artwork_size": "175 x 120 ซม.",
        "artwork_technique": "จิตรกรรมผสม",
        "exhibition_name": "การแสดงศิลปกรรมแห่งชาติ ครั้งที่ 51 พ.ศ. 2548",
        "award_name": "รางวัลประกาศนียบัตรเกียรตินิยม อันดับ 1 เหรียญทอง (จิตรกรรม)",
        "license": "มหาวิทยาลัยศิลปากร",
        "concept": "ชีวิตที่ผ่านมา และเวลาที่ผ่านไปของแม่นั้น เป็นระยะเวลานานมาแล้ว ผ่านร้อน ผ่านหนาว ผ่านฝน ผ่านทุกข์ ผ่านสุข และผ่านสิ่งต่าง ๆ มากมาย ตามวิสัยของปุถุชน ชีวิตของมนุษย์ทุกผู้ทุกนามไม่ว่ายากดีมีจนสุดท้ายทั้งหมดลงที่ความแก่ ความเจ็บ ความตาย ทั้งนั้น",
        "detail": "ดูแลและจัดการ : หอศิลป์ มหาวิทยาลัยศิลปากร\nสถานที่ตั้ง : หอศิลป์สนามจันทร์",
        "image_url": "http://www.resource.lib.su.ac.th/awardsu/artimages/0000251.jpg",
        "url": "http://www.resource.lib.su.ac.th/awardsu/web/artdetail?item_id=251",
    },
]
# artworks.append()

# เพิ่มข้อมูลตัวอย่างในตาราง "Artworks"
# try:
#     for art in artworks:
#         cursor.execute("""
#             INSERT INTO Artworks (artwork_name, artist_name, artwork_type, artwork_size, artwork_technique, exhibition_name, award_name, license, concept, detail, image_url, url)
#             SELECT ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
#             WHERE NOT EXISTS (SELECT 1 FROM Artworks WHERE artwork_name = ?)
#         """, (
#             art["artwork_name"], art["artist_name"], art["artwork_type"], art["artwork_size"],
#             art["artwork_technique"], art["exhibition_name"], art["award_name"],
#             art["license"], art["concept"], art["detail"], art["image_url"], art["url"], art["artwork_name"]
#         ))
# except Exception as e:
#     print(e)
#     conn.commit()
#     conn.close()


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
