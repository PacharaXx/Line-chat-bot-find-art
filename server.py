import uvicorn
from fastapi import FastAPI, Request
from linebot import LineBotApi, WebhookHandler
from linebot.models import ImageSendMessage
from bot import ImgSearchBotLine
from imageSearch import ImageSearcher
from PIL import Image
from dotenv import load_dotenv
import os
import logging
from fastapi.responses import FileResponse
import time
import sys

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


@app.get('/')
async def index():
    return {'message': 'Hello, World!'}

# Define a route to handle webhook requests
@app.post("/webhook")
async def webhook(request: Request):
    # Parse the webhook event
    body = await request.json()
    # Get the X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    
    global users_data
    events = body['events']
    current_time = time.time()
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
    print(log_message)
    
    # Handle webhook body
    try:
        if body['events'][0]['message']['type'] == 'text':
            user_id = body['events'][0]['source']['userId']
            message = body['events'][0]['message']['text']

            print(events)
            if message == 'ค้นหาด้วยภาพ':
                # display log in terminal
                print(user_id)
                print(message)
                # ImgSearchBotLine.push(user_id, 'ส่งภาพมาเลยจ้า')
                reply_token = body['events'][0]['replyToken']
                result = BotLine.reply(reply_token, message)

                # Check the result
                if result == 'Success':
                    users_data.append({'user_id': user_id, 'Phase': 'Waiting for image'})
                    print("Reply sent successfully.")
                else:
                    print("Reply sending failed. Error:", result)
                users_data.append({'user_id': user_id, 'Phase': 'Waiting for image'})
                return {'message': 'success'}

        # if it's a image and map find if user_id in users_data and phase is 'Waiting for image'
        elif body['events'][0]['message']['type'] == 'image' and len(list(filter(lambda x: x['user_id'] == body['events'][0]['source']['userId'] and x['Phase'] == 'Waiting for image', users_data))) > 0:
            print('Its a image !!!!!')
            user_id = body['events'][0]['source']['userId']
            image_id = body['events'][0]['message']['id']
            image_content = line_bot_api.get_message_content(image_id)
            # Test the API with a sample image file
            try:
                with open(f'./imgTarget/{image_id}.jpg', 'wb') as f:
                    for chunk in image_content.iter_content():
                        f.write(chunk)
            except Exception as e:
                # if not found folder imgTarget
                os.mkdir('./imgTarget')
                with open(f'./imgTarget/{image_id}.jpg', 'wb') as f:
                    for chunk in image_content.iter_content():
                        f.write(chunk)
            # Test the API with a sample image file
            try:
                image_searcher.set_target(Image.open(f'.imgTarget/{image_id}.jpg'))
                print('set target success')
            except Exception as e:
                # if not found folder imgTarget
                print(e)
                return {'message': 'error'}
            starttime = time.time()
            response = image_searcher.run_test()
            print('Response: ', response)
            # response is json
            # in format [{'most_similar_image_path': most_similar_image_path, 'score': score}, ...]
            # most_similar_image_path is path of image
            # score is score of image
            # get image from response and send to user
            for i in range(len(response)):
                # get image from response
                image_path = response[i]['most_similar_image_path']
                image_name = image_path.split('/')[-1]
                print('image_name: ', image_name)
                # send image to user
                line_bot_api.push_message(
                    user_id,
                    ImageSendMessage(
                        original_content_url=f' https://d776-154-197-124-214.ngrok-free.app/imgsearch/{image_name}',
                        preview_image_url=f' https://d776-154-197-124-214.ngrok-free.app/imgsearch/{image_name}'
                    )
                )
                print('send image success')

            totaltime = time.time() - starttime
            print('totaltime to find: ', totaltime)
            # change phase to 'Image sent'
            users_data = list(map(lambda x: {'user_id': x['user_id'], 'Phase': 'Image sent'} if x['user_id'] == user_id else x, users_data))
            users_data.remove({'user_id': user_id, 'Phase': 'Image sent'})
            print('Image sent')
            # print users_data
            print(users_data)
            return {'message': 'success'}
        else:
            print('else')
            # return status 200
            return {'message': 'success'}

    except Exception as e:
        print(e)
        return {'message': 'error'}
    return {'message': 'success'}


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

# Define a route to handle image requests.
@app.get('/{image_name}')
async def handle_image_target(image_name: str):
    # Show the image.
    return FileResponse(f'./{image_name}')
    

# Start the FastAPI server.
if __name__ == '__main__':
    # create instance of ImageSearcher
    image_searcher = ImageSearcher()
    image_searcher.set_model('clip-ViT-B-32')
    image_searcher.load_model()
    logging.info('load model success')

    # # Load the image names jpg and jpeg
    # image_names = list(glob.glob('./imgsearch/*.jpg') + glob.glob('./imgsearch/*.jpeg') + glob.glob('./imgsearch/*.png'))
    # # Set the image names
    # image_searcher.set_image_names(image_names)
    # logging.info('set image_names success')

    # Load the encoded images
    image_searcher.load_images()
    logging.info('load images success')

    BotLine = ImgSearchBotLine(token, chanel_secret)
    
    try:
        uvicorn.run(app, host='localhost', port=8080)
    except Exception as e:
        print(e)
        exit(0)
