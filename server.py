import uvicorn
import subprocess
from fastapi import FastAPI, Request
from linebot import LineBotApi, WebhookHandler
from bot import ImgSearchBotLine
from imageSearch import ImageSearcher
from detection import ImageProcessor
from PIL import Image
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

# Load .env file
load_dotenv('./.env')
ip: str = os.getenv('IP')
token: str = os.getenv('TOKEN')
chanel_secret: str = os.getenv('CHANNEL_SECRET')

# Create a new FastAPI instance.
app = FastAPI()

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
BotLine = ImgSearchBotLine(token, chanel_secret)

class UserDataManager:
    def __init__(self):
        self.users_data = {}
        self.locks = {}
        self.load_users_data()

    def load_users_data(self):
        with open('./users_data.json', 'r') as file:
            try:
                self.users_data = json.load(file)
            except:
                self.users_data = {}

    async def update_user_phase(self, user_id, phase):
        async with self.get_lock(user_id):
            if user_id not in self.users_data:
                self.users_data[user_id] = {'user_id': user_id, 'Phase': phase}
            else:
                if phase == 'Image Sent':
                    # remove user from users_data
                    del self.users_data[user_id]
                self.users_data[user_id]['Phase'] = phase

        with open('./users_data.json', 'w') as file:
            json.dump(list(self.users_data.values()), file)

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
                    # update user phase
                    user_data_manager.update_user_phase(user_id, 'Waiting for image')
                    logging.info(log_message)
                else:
                    print("Reply sending failed. Error:", result)
                return {'message': 'success'}
            
            elif message == 'c':
                try:
                    # ImgSearchBotLine.push(user_id, 'ส่งภาพมาเลยจ้า')
                    reply_token = body['events'][0]['replyToken']
                    caraousel = ImgSearchBotLine.create_carousel()
                    x = BotLine.push_flex(user_id, caraousel)
                    if x == 'Success':
                        print("Reply sent successfully.")
                    else:
                        print("Reply sending failed. Error:", x)
                except Exception as e:
                    print(e)
                    return {'message': 'error'}

                return {'message': 'success'}
            
        elif body['events'][0]['message']['type'] == 'image' and user_data_manager.users_data.get(user_id, {}).get('Phase', 'None') == 'Waiting for image':
            user_id = body['events'][0]['source']['userId']
            image_id = body['events'][0]['message']['id']
            image_content = line_bot_api.get_message_content(image_id)

            starttime = time.time()
            
            # send to crop in ImgArgumentation
            imgArgumentation = ImageProcessor()
            imgArgumentation.set_img(Image.open(io.BytesIO(image_content.content)))
            image_content = imgArgumentation.preprocess_and_crop_image()
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
            caraousel = ImgSearchBotLine.create_carousel(flex_data)
            # send carousel to user
            x = BotLine.push_flex(user_id, caraousel)
            if x == 'Success':
                print("Reply sent successfully.")
            else:
                print("Reply sending failed. Error:", x)
            # update user phase
            user_data_manager.update_user_phase(user_id, 'Image Sent')
            print('Image sent')
            # ------- for debug -------
            print(log_message)
            logging.info(log_message)
            totaltime = time.time() - starttime
            print('Total Time:', totaltime)
            return {'message': 'success'}
        else:
            print('else')
            # return status 200
            return {'message': 'success'}
    except Exception as e:
        print(e)
        return {'message': 'error'}
    finally:
        print('finally')
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
    image_path = f'./imgsearch/{image_name}'  # กำหนดที่อยู่ของไฟล์ภาพ
    if os.path.exists(image_path):
        return FileResponse(image_path)  # ส่งไฟล์ภาพกลับไปยังผู้ใช้งาน
    else:
        return {"message": "Image not found"}  # ถ้าไม่พบไฟล์ภาพ ส่งข้อความกลับไปยังผู้ใช้งาน
    
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

    num_cpus = os.cpu_count()
    print(f'Number of CPUs: {num_cpus}')
    try:
        # uvicorn.run('server:app', host='localhost', port=8080, reload=True, workers=num_cpus)
        # ------------------ for deploy ------------------
        num_workers = num_cpus - 1 if num_cpus > 1 else 1
        subprocess.run(["gunicorn", "-w", str(num_workers), "-k", "uvicorn.workers.UvicornWorker", "server:app"])
    except Exception as e:
        print(e)
        exit(0)

