import uvicorn
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

users_data = []
# users_data = [{'user_id': 1, 'Phase': 'Waiting for image'}, {'user_id': 2, 'Phase': 'Waiting for image'}]

# Suppress warning messages
warnings.filterwarnings("ignore", category=LineBotSdkDeprecatedIn30)

image_searcher = ImageSearcher()
image_searcher.set_model('clip-ViT-B-32')
logging.info('set model success')
image_searcher.load_model()
logging.info('load model success')
BotLine = ImgSearchBotLine(token, chanel_secret)


@app.get('/')
async def index():
    return {'message': 'Hello, World!'}

async def process(body):
    global users_data
    events = body['events']
    # date and time in format Day month year,HH:MM:SS
    current_time = time.strftime("%a %b %d %Y,%H:%M:%S", time.localtime())
    user_id = body['events'][0]['source']['userId']
    message_type = (body['events'][0]['message']['type']) if body['events'][0]['message']['type'] == 'text' else (body['events'][0]['message']['type']) if body['events'][0]['message']['type'] == 'image' else 'None'
    message_body = (body['events'][0]['message']['text']) if body['events'][0]['message']['type'] == 'text' else 'None'
    matching_users = list(filter(lambda x: x['user_id'] == user_id, users_data))

    log_message = (
        f"---------Webhook Event---------\n"
        f"Current Time: {current_time}\n"
        f"UserID: {user_id}\n"
        f"Message Type: {message_type}\n"
        f"Message Text: {message_body}\n"
        f"Matching Users: {matching_users}\n"
        f"Phase: {(matching_users[0]['Phase'] if matching_users[0]['Phase'] else 'None') if len(matching_users) > 0 else 'None'}\n"
        f"--------------------------------\n"
    )
    
    # Handle webhook body
    try:
        if body['events'][0]['message']['type'] == 'text':
            user_id = body['events'][0]['source']['userId']
            message = body['events'][0]['message']['text']

            if message == 'ค้นหาด้วยภาพ':
                # ImgSearchBotLine.push(user_id, 'ส่งภาพมาเลยจ้า')
                reply_token = body['events'][0]['replyToken']
                result = BotLine.reply(reply_token, message)

                # Check the result
                if result == 'Success':
                    users_data.append({'user_id': user_id, 'Phase': 'Waiting for image'})
                    print("Reply sent successfully.")
                    print(log_message)
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
            
        elif body['events'][0]['message']['type'] == 'image' and len(list(filter(lambda x: x['user_id'] == body['events'][0]['source']['userId'] and x['Phase'] == 'Waiting for image', users_data))) > 0:
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
            # change phase to 'Image sent'
            users_data[users_data.index({'user_id': user_id, 'Phase': 'Waiting for image'})]['Phase'] = 'Image sent'
            # remove user_id and phase in users_data
            users_data.remove({'user_id': user_id, 'Phase': 'Image sent'})
            print('Image sent')
            # print users_data
            print('Users Data:', users_data)
            print(log_message)
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
    # Show the image.
    return FileResponse(f'./imgsearch/{image_name}')
    
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

    try:
        uvicorn.run('server:app', host='localhost', port=8080, reload=True)
    except Exception as e:
        print(e)
        exit(0)

