import requests
import json

def getimgurlfromjson(jsonurl):
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
    imgurllist = []
    with open(jsonurl, 'r') as f:
        data = json.load(f)
        for i in data:
            imgurllist.append(i['Image'])
    return imgurllist


# ทดสอบโปรแกรม
# load json file from local
jsonurl = './data.json'
imgurllist = getimgurlfromjson(jsonurl)
# save image from url into folder 'imgsearch' and file name is last part of url
for i in imgurllist:
    imgname = i.split('/')[-1]
    img = requests.get(i)
    with open('imgsearch/'+imgname, 'wb') as f:
        f.write(img.content)
        print('save image: ', imgname)