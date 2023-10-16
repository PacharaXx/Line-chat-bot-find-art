import cv2
import numpy as np
import os

# ฟังก์ชันสำหรับการแยกประเภทของรูปภาพตามสีหลักของภาพ HSI
def categorize_images_by_primary_color(input_folder, output_folder):
    # สร้างโฟลเดอร์ปลายทางถ้ายังไม่มี
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith((".jpg", ".jpeg", ".png")):
            image_path = os.path.join(input_folder, filename)
            img = cv2.imread(image_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # หาสีหลักของภาพศิลปะ
            hsi = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
            h, s, i = cv2.split(hsi)
            h = h.flatten()
            s = s.flatten()
            i = i.flatten()
            hist, _ = np.histogram(h, bins=180)
            primary_color = np.argmax(hist)

            # แปลงสีหลักเป็นชื่อสี
            if primary_color >= 0 and primary_color < 10:
                category = "red"
            elif primary_color >= 10 and primary_color < 20:
                category = "orange"
            elif primary_color >= 20 and primary_color < 30:
                category = "yellow"
            elif primary_color >= 30 and primary_color < 50:
                category = "green"
            elif primary_color >= 50 and primary_color < 70:
                category = "cyan"
            elif primary_color >= 70 and primary_color < 100:
                category = "blue"
            elif primary_color >= 100 and primary_color < 130:
                category = "purple"
            elif primary_color >= 130 and primary_color < 150:
                category = "pink"
            elif primary_color >= 150 and primary_color < 180:
                category = "red"

            # สร้างโฟลเดอร์ปลายทางสำหรับแต่ละประเภทสี
            category_folder = os.path.join(output_folder, category)
            if not os.path.exists(category_folder):
                os.makedirs(category_folder)

            # บันทึกรูปภาพในโฟลเดอร์ปลายทางที่เป็นชื่อของสีหลัก
            output_path = os.path.join(category_folder, filename)
            cv2.imwrite(output_path, img)

if __name__ == "__main__":
    input_folder = "./imgsearch/"  # ระบุโฟลเดอร์ที่เก็บรูปภาพที่ต้องการแยกประเภท
    output_folder = "output_images_folder"  # ระบุโฟลเดอร์ปลายทางที่จะเก็บรูปภาพที่แยกแต่ละประเภท
    categorize_images_by_primary_color(input_folder, output_folder)
