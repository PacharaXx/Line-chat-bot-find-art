import uvicorn
from fastapi import FastAPI, Request
from linebot import LineBotApi, WebhookHandler
from bot import ImgSearchBotLine
from imageSearch import ImageSearcher
import glob
from PIL import Image
from dotenv import load_dotenv
import os
import logging

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
    signature = request.headers['X-Line-Signature']
    events = body['events']
    print(events)
    global users_data
    # Handle webhook body
    try:
        if body['events'][0]['message']['type'] == 'text':
            user_id = body['events'][0]['source']['userId']
            message = body['events'][0]['message']['text']

            if message == 'ค้นหาด้วยภาพ':
                ImgSearchBotLine.push(user_id, 'ส่งภาพมาเลยจ้า')
                users_data.append({'user_id': user_id, 'Phase': 'Waiting for image'})
                return {'message': 'success'}

        # if it's a image
        elif body['events'][0]['message']['type'] == 'image' and map(lambda x: x['Phase'], filter(lambda x: x['user_id'] == user_id, users_data)) == 'Waiting for image':
            print('Its a image !!!!!')
            user_id = body['events'][0]['source']['userId']
            image_id = body['events'][0]['message']['id']
            image_content = line_bot_api.get_message_content(image_id)
            with open(f'./{image_id}.jpg', 'wb') as f:
                for chunk in image_content.iter_content():
                    f.write(chunk)
            # Test the API with a sample image file
            image_searcher.set_target(Image.open(f'./{image_id}.jpg'))
            logging.info('set target success')
            response = image_searcher.run_test()
            print(response)
            # change image path all in response to image url
            most_similar_image_path = list(map(lambda x: f'https://{ip}/{x}', response))
            # most_similar_image_path = list(map(lambda x: f'https://{ip}/imgsearch/{x}', response))
            print(most_similar_image_path)
            # send image to user
            ImgSearchBotLine.push_image(user_id, most_similar_image_path[0])
            ImgSearchBotLine.push_image(user_id, most_similar_image_path[1])
            ImgSearchBotLine.push_image(user_id, most_similar_image_path[2])
            users_data.append({'user_id': user_id, 'Phase': 'Image sent'})
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
    

# Start the FastAPI server.
if __name__ == '__main__':
    # create instance of ImageSearcher
    image_searcher = ImageSearcher()
    image_searcher.set_model('clip-ViT-B-32')
    image_searcher.load_model()
    logging.info('load model success')

    # Load the image names jpg and jpeg
    image_names = list(glob.glob('./imgsearch/*.jpg') + glob.glob('./imgsearch/*.jpeg') + glob.glob('./imgsearch/*.png'))
    # Set the image names
    image_searcher.set_image_names(image_names)
    logging.info('set image_names success')

    # Load the encoded images
    image_searcher.load_images()
    logging.info('load images success')

    BotLine = ImgSearchBotLine(token, chanel_secret)
    
    try:
        uvicorn.run(app, host=ip, port=3333)
    except Exception as e:
        print(e)
        exit(0)
