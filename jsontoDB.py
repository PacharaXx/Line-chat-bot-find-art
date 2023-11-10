import json
import sqlite3
from imageSearch import ImageSearcher

def jsontoDB():
    # get data from json file
    with open('data.json', 'r') as f:
        data = json.load(f)
    # connect to database sqlite3
    db = sqlite3.connect('test1.db')
    cursor = db.cursor()
    # insert data into table Artworks
    # {
    #     "Artwork_Name": "\"ร่างกายแม่\" (แม่) หมายเลข 2",
    #     "Artist_Name": "อัฐพร นิมมาลัยแก้ว",
    #     "Artwork_Type": "จิตรกรรม",
    #     "Artwork_Size": "175 x 120 ซม.",
    #     "Artwork_Technique": "จิตรกรรมผสม",
    #     "Exhibition_Name": "การแสดงศิลปกรรมแห่งชาติ ครั้งที่ 51 พ.ศ. 2548",
    #     "Award_Name": "รางวัลประกาศนียบัตรเกียรตินิยม อันดับ 1 เหรียญทอง (จิตรกรรม)",
    #     "License": "มหาวิทยาลัยศิลปากร",
    #     "Concept": "ชีวิตที่ผ่านมา และเวลาที่ผ่านไปของแม่นั้น เป็นระยะเวลานานมาแล้ว ผ่านร้อน ผ่านหนาว ผ่านฝน ผ่านทุกข์ ผ่านสุข และผ่านสิ่งต่าง ๆ มากมาย ตามวิสัยของปุถุชน ชีวิตของมนุษย์ทุกผู้ทุกนามไม่ว่ายากดีมีจนสุดท้ายทั้งหมดลงที่ความแก่ ความเจ็บ ความตาย ทั้งนั้น",
    #     "Detail": "ดูแลและจัดการ : หอศิลป์ มหาวิทยาลัยศิลปากร\nสถานที่ตั้ง : หอศิลป์สนามจันทร์",
    #     "Image": "http://www.resource.lib.su.ac.th/awardsu/artimages/0000251.jpg",
    #     "URL": "http://www.resource.lib.su.ac.th/awardsu/web/artdetail?item_id=251"
    # },
    for art in data:
        try:
            # insert data into table Artworks
            cursor.execute(
                """
                INSERT OR REPLACE INTO Artworks (artwork_name, artist_name, artwork_type, artwork_size, artwork_technique, exhibition_name, award_name, license, concept, detail, image_url, url)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    art['Artwork_Name'],
                    art['Artist_Name'],
                    art['Artwork_Type'],
                    art['Artwork_Size'],
                    art['Artwork_Technique'],
                    art['Exhibition_Name'],
                    art['Award_Name'],
                    art['License'],
                    art['Concept'],
                    art['Detail'],
                    art['Image'],
                    art['URL']
                )
            )
            db.commit()
            print('insert data into table Artworks success')
        except Exception as e:
            print(e)
            pass

if __name__ == '__main__':
    jsontoDB()
    