import uvicorn
import sqlite3
from fastapi import FastAPI, File, Request
from linebot import LineBotApi, WebhookHandler
from bot import ImgSearchBotLine
from imageSearch import ImageSearcher
from detection import ImageProcessor
import cv2
import numpy as np
from dotenv import load_dotenv
import os
import logging
from fastapi.responses import FileResponse
import time
import warnings
from linebot import LineBotSdkDeprecatedIn30
import io
from fastapi import BackgroundTasks
import json
import asyncio
import multiprocessing
from pathlib import Path
# เพิ่มการใช้ caching เพื่อลดการเรียกใช้งานไฟล์ที่มีการเข้าถึงซ้ำซ้อน
from fastapi.staticfiles import StaticFiles
from fastapi import Form, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
# Load .env file
load_dotenv('./.env')
ip: str = os.getenv('IP')
token: str = os.getenv('TOKEN')
chanel_secret: str = os.getenv('CHANNEL_SECRET')
ip_url: str = os.getenv('IP_URL')
print('IP:', ip)
print('IP_URL:', ip_url)


# Create a new FastAPI instance.
app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

# กำหนด path สำหรับเก็บไฟล์และเปิดใช้ caching
app.mount("/imgsearch", StaticFiles(directory="./imgsearch", html=False), name="imgsearch")

# Create a new LineBotApi object
line_bot_api = LineBotApi(token)

# Create a new WebhookHandler object
webhook_handler = WebhookHandler(chanel_secret)

# Suppress warning messages
warnings.filterwarnings("ignore", category=LineBotSdkDeprecatedIn30)

# logging in json format file
# [{time: time, level: level, message: message}, ...]
logging.basicConfig(filename='./log.json', filemode='a', format='%(asctime)s %(levelname)s %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

image_searcher = ImageSearcher()
image_searcher.set_model('clip-ViT-B-32')
logging.info('set model success')
image_searcher.load_model()
logging.info('load model success')
BotLine = ImgSearchBotLine(token, chanel_secret, ip_url)

class UserDataManager:
    def __init__(self):
        self.users_data = {}
        self.locks = {}
        self.load_users_data()

    def load_users_data(self):
        try:
            with open('./users_data.json', 'r', encoding='utf-8') as file:
                self.users_data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.users_data = {}

    async def update_user_phase(self, user_id, phase):
        async with await self.get_lock(user_id):
            self.users_data[user_id] = {'Phase': phase}
            await self.save_users_data()

    async def save_users_data(self):
        # Write user data to file asynchronously
        with open('./users_data.json', 'w', encoding='utf-8') as file:
            json.dump(self.users_data, file, ensure_ascii=False, indent=4)

    async def remove_user_data(self, user_id):
        async with await self.get_lock(user_id):
            if user_id in self.users_data:
                del self.users_data[user_id]
                await self.save_users_data()

    async def get_lock(self, user_id):
        if user_id not in self.locks:
            self.locks[user_id] = asyncio.Lock()
        return self.locks[user_id]

@app.get('/')
async def index():
    return {'message': 'Hello, World!'}

# Create an instance of UserDataManager
user_data_manager = UserDataManager()

async def process(body):
    # Get the event type
    events = body['events']
    # date and time in format Day month year,HH:MM:SS
    current_time = time.strftime("%a %b %d %Y,%H:%M:%S", time.localtime())
    user_id = body['events'][0]['source']['userId']
    message_type = (body['events'][0]['message']['type']) if body['events'][0]['message']['type'] == 'text' else (body['events'][0]['message']['type']) if body['events'][0]['message']['type'] == 'image' else 'None'
    message_body = (body['events'][0]['message']['text']) if body['events'][0]['message']['type'] == 'text' else 'None'

    log_message = (
        f"---------Webhook Event---------\n"
        f"Current Time: {current_time}\n"
        f"UserID: {user_id}\n"
        f"Message Type: {message_type}\n"
        f"Message Text: {message_body}\n"
        f"Phase: {user_data_manager.users_data.get(user_id, {}).get('Phase', 'None')}\n"
        f"--------------------------------\n"
    )
    
    # Handle webhook body
    try:
        if body['events'][0]['message']['type'] == 'text':
            user_id = body['events'][0]['source']['userId']
            message = body['events'][0]['message']['text']
            logging.info('Receive message from UserID: ' + user_id + ' Message: ' + message)
            if message == 'ค้นหาด้วยภาพ':
                # ImgSearchBotLine.push(user_id, 'ส่งภาพมาเลยจ้า')
                reply_token = body['events'][0]['replyToken']
                result = BotLine.reply(reply_token, message)

                # Check the result
                if result == 'Success':
                    print("Reply sent successfully.")
                    user_data_manager.users_data[user_id] = {'Phase': 'Waiting for image'}
                    await user_data_manager.save_users_data()
                    logging.info(log_message)
                else:
                    print("Reply sending failed. Error:", result)
                return {'message': 'success'}
        
            print(user_data_manager.users_data.get(user_id, {}).get('Phase', 'None'))
        elif body['events'][0]['message']['type'] == 'image' and user_data_manager.users_data.get(user_id, {}).get('Phase', 'None') == 'Waiting for image':
            user_id = body['events'][0]['source']['userId']
            image_id = body['events'][0]['message']['id']
            image_content = line_bot_api.get_message_content(image_id)

            logging.info('Receive image from UserID: ' + user_id + ' ImageID: ' + image_id)
            starttime = time.time()
            
            # send to crop in ImgArgumentation
            imgArgumentation = ImageProcessor()
            # Get the image content
            image_bytes = image_content.content
            # Convert the image data to a format that OpenCV can read
            nparr = np.frombuffer(image_bytes, np.uint8)
            img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            img_rgb = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
            imgArgumentation.set_img(img_rgb)
            endtime = time.time()
            print('Set image time and convert to RGB:', endtime - starttime)
            image_content = imgArgumentation.preprocess_and_crop_image()
            endtime = time.time()
            print('Preprocess and crop image time:', endtime - starttime)
            try:
                image_searcher.set_target(image_content)
                print('set target success')
            except Exception as e:
                print(e)
                return {'message': 'error'}
            response = image_searcher.run_test()
            # response is json
            # in format [{'most_similar_image_path': most_similar_image_path, 'score': score}, ...]
            # most_similar_image_path is path of image
            # score is score of image
            # get image from response and send to user  
            flex_data = []
            for data in response:
                print(f'Artwork ID: {data["artwork_id"]} Artwork Name: {data["artwork_name"]} Score: {data["score"]}')
                flex_data.append({'artwork_id': data['artwork_id'],
                                'artwork_name': data['artwork_name'],
                                'artist_name': data['artist_name'],
                                'artwork_type': data['artwork_type'],
                                'artwork_size': data['artwork_size'],
                                'artwork_technique': data['artwork_technique'],
                                'exhibition_name': data['exhibition_name'],
                                'award_name': data['award_name'],
                                'license': data['license'],
                                'concept': data['concept'],
                                'detail': data['detail'],
                                'image_url': data['image_url'],
                                'url': data['url'],
                                'score': data['score']})
            # create carousel
            caraousel = BotLine.create_carousel(flex_data)
            # send carousel to user
            x = BotLine.push_flex(user_id, caraousel)
            if x == 'Success':
                print("Reply sent successfully.")
            else:
                print("Reply sending failed. Error:", x)
            # update user phase
            await user_data_manager.update_user_phase(user_id, 'Waiting for image')
            print('Image sent')
            # ------- for debug -------
            print(log_message)
            logging.info(log_message)
            totaltime = time.time() - starttime
            print('Total Time:', totaltime)
            # -------------------------
            # remove user data
            await user_data_manager.remove_user_data(user_id)
            return {'message': 'success'}
        else:
            user_id = body['events'][0]['source']['userId']
            message_body = (body['events'][0]['message']['text']) if body['events'][0]['message']['type'] == 'text' else 'None'
            logging.info('Receive message from UserID: ' + user_id + ' Message: ' + message_body)
            print('No action')
            # return status 200
            return {'message': 'success'}
    except Exception as e:
        print(e)
        return {'message': 'error'}
    # return status 200
    return {'message': 'success'}

# Define a route to handle webhook requests
@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    # Parse the webhook event
    body = await request.json()
    # Get the X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # Handle webhook body test
    # try:
    #     webhook_handler.handle(body, signature)
    # except Exception as e:
    #     print(e)
    #     return {'message': 'error'}
    # return {'message': 'success'}
    print('Have a new request!!')
    background_tasks.add_task(process, body)
    return {"message": "Notification sent in the background"}
    # processing = await process(body)
    # return processing

# Define a route to handle user requests.
@app.post('/user/{user_id}')
async def handle_user(user_id: int):
    # Do some processing.
    # Return a response to the user.
    return {'message': 'Request received '+str(user_id)}

# Define a route to handle image requests.
@app.get('/imgsearch/{image_name}')
async def handle_image(image_name: str):
    image_path = Path(f'./imgsearch/{image_name}')  # กำหนดที่อยู่ของไฟล์ภาพ
    
    if image_path.is_file():
        return FileResponse(image_path)  # ส่งไฟล์ภาพกลับไปยังผู้ใช้งาน
    else:
        return {"message": "Image not found"}  # ถ้าไม่พบไฟล์ภาพ ส่งข้อความกลับไปยังผู้ใช้งาน
    
@app.get('/report')
async def report():
    # return web page
    return FileResponse('./report.html')

@app.post("/submit_report")
async def submit_report(header: str = Form(...), report: str = Form(...), image: UploadFile = File(...)):
    try:
        upload_folder = "./uploaded_images"
        os.makedirs(upload_folder, exist_ok=True)
        
        image_path = os.path.join(upload_folder, image.filename)
        with open(image_path, "wb") as buffer:
            buffer.write(image.file.read())
        
        conn = sqlite3.connect('report.db')
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS reports (id INTEGER PRIMARY KEY AUTOINCREMENT, header TEXT, report TEXT, image_filename TEXT)')
        
        cursor.execute('INSERT INTO reports (header, report, image_filename) VALUES (?, ?, ?)', (header, report, image.filename))
        last_inserted_id = cursor.lastrowid
        
        new_image_filename = f"{last_inserted_id}.jpg"
        os.rename(image_path, os.path.join(upload_folder, new_image_filename))
        
        cursor.execute('UPDATE reports SET image_filename = ? WHERE id = ?', (new_image_filename, last_inserted_id))
        conn.commit()
        conn.close()

        return JSONResponse(content={"message": "Report submitted successfully"})
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Error: {str(e)}"})


# Start the FastAPI server.
if __name__ == '__main__':
    # # Suppress warning messages
    # warnings.filterwarnings("ignore", category=LineBotSdkDeprecatedIn30)

    # image_searcher = ImageSearcher()
    # image_searcher.set_model('clip-ViT-B-32')
    # logging.info('set model success')
    # image_searcher.load_model()
    # logging.info('load model success')
    # BotLine = ImgSearchBotLine(token, chanel_secret)

    # # Load the image names jpg and jpeg
    # image_names = list(glob.glob('./imgsearch/*.jpg') + glob.glob('./imgsearch/*.jpeg') + glob.glob('./imgsearch/*.png'))
    # # Set the image names
    # image_searcher.set_image_names(image_names)
    # logging.info('set image_names success')

    # Load the encoded images
    # image_searcher.load_images()
    # logging.info('load images success')

    # Create a new ImgSearchBotLine object


    num_cpus = multiprocessing.cpu_count()
    try:
        # num_workers = num_cpus - 1 if num_cpus > 1 else 1
        # print(f'Number of workers: {num_workers}')
        uvicorn.run('server:app', host=ip, port=8080)
        # uvicorn.run('server:app', host='localhost', port=8080,ssl_keyfile='./key.pem', ssl_certfile='./cert.pem')
        # subprocess.run(["uvicorn", "server:app", "--host", "localhost", "--port", "8080", "--workers", str(num_workers)])
    except Exception as e:
        print('Launch server failed:', e)
        exit(0)

