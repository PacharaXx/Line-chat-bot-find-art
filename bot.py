from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage, ImageSendMessage, FlexSendMessage, StickerSendMessage

#  pip install line-bot-sdk
from linebot import LineBotSdkDeprecatedIn30
import warnings
import os
from dotenv import load_dotenv

import json

load_dotenv('./.env')
ip_url: str = os.getenv('IP_URL')

class ImgSearchBotLine:
    def __init__(self, channel_access_token, channel_secret, ip_url):
        # Suppress warning messages
        warnings.filterwarnings("ignore", category=LineBotSdkDeprecatedIn30)
        self.line_bot_api = LineBotApi(channel_access_token)
        self.handler = WebhookHandler(channel_secret)
        self.ip = ip_url+'imgsearch/'

    def reply(self, reply_token, message):
        try:
            self.line_bot_api.reply_message(reply_token, TextSendMessage(text=message))
            return "Success"
        except Exception as e:
            return e

    def push(self, user_id, message):
        try:
            self.line_bot_api.push_message(user_id, TextSendMessage(text=message))
            return "Success"
        except Exception as e:
            return e

    def push_image(self, user_id, image_path):
        try:
            self.line_bot_api.push_message(
                user_id,
                ImageSendMessage(
                    original_content_url=image_path, preview_image_url=image_path
                ),
            )
            return "Success"
        except Exception as e:
            return e
        
    def push_sticker(self, user_id, package_id, sticker_id):
        try:
            self.line_bot_api.push_message(
                user_id,
                StickerSendMessage(
                    package_id=package_id, sticker_id=sticker_id
                ),
            )
            return "Success"
        except Exception as e:
            print('Sticker Error: ', e)
            return e

    def push_flex(self, user_id, flex):
        try:
            self.line_bot_api.push_message(user_id, FlexSendMessage(alt_text="เจอแล้วว!!", contents=flex))
            return "Success"
        except Exception as e:
            return e

    def create_carousel(self, response):
        try:
            contents = []
            carousel = {"type": "carousel", "contents": contents}
            for data in response:
                if 'http' in data["image_url"]:
                    url = data["image_url"].split("/")[-1]
                else:
                    url = data["image_url"]
                url = self.ip + url
                if 'http' not in data["url"]:
                    data["url"] = f'{ip_url}imgsearch/' + data["url"]
                    print('URI: ', data["url"])
                uri = data["url"]
                print('URL: ', url)

                bubble_content = {
                    "type": "bubble",
                    "hero": {
                        "type": "image",
                        "url": url,
                        "size": "full",
                        "aspectRatio": "20:13",
                        "aspectMode": "cover",
                        "action": {
                        "type": "uri",
                        "uri": uri
                        }
                    },
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "sm",
                        "contents": [
                            #             
                        ]
                    },
                    "footer": {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "sm",
                        "contents": [
                        {
                            "type": "button",
                            "action": {
                            "type": "uri",
                            "label": "ดูข้อมูลเพิ่มเติม",
                            "uri": data["url"]
                            },
                            "color": "#00D00FFF",
                            "style": "primary"
                        }
                        ]
                    },
                      "size": "deca",
                    }
                
                for key in data:
                    # check len of body contents
                    lenOfBody = len(bubble_content["body"]["contents"])
                    if lenOfBody == 0:
                        weight = 'bold'
                        size = 'md'
                    else:
                        weight = 'regular'
                        size = 'sm'
                    if isinstance(data[key], str) and key == 'artwork_name' and (data[key] != 'NONE'):
                        # if len(data[key]) > 15:
                        #     data[key] = data[key][:15] + '...'
                        # inset box into contents
                        bubble_content["body"]["contents"].insert(lenOfBody, {
                            "type": "box",
                            "layout": "baseline",
                            "contents": [
                            {
                                "type": "text",
                                "text": data["artwork_name"],
                                "weight": weight,
                                "size": size,
                                "flex": 1,
                                "wrap": True,
                                "contents": []
                            }
                            ]
                        })
                    elif isinstance(data[key], str) and key == 'artist_name':
                        if data[key] != 'NONE':
                            # if len(data[key]) > 20:
                            #     data[key] = data[key][:20] + '...'
                            # inset box into contents
                            bubble_content["body"]["contents"].insert(lenOfBody, {
                                "type": "box",
                                "layout": "baseline",
                                "contents": [
                                {
                                    "type": "text",
                                    "text": data["artist_name"],
                                    "weight": weight,
                                    "size": size,
                                    "style": "italic",
                                    "flex": 0,
                                    "wrap": True,
                                    "contents": []
                                }
                                ]
                            })
                        else:
                            if data["license"] != 'NONE':
                                bubble_content["body"]["contents"].insert(lenOfBody, {
                                    "type": "box",
                                    "layout": "baseline",
                                    "contents": [
                                    {
                                        "type": "text",
                                        "text": data["license"],
                                        "weight": weight,
                                        "size": size,
                                        "style": "italic",
                                        "flex": 0,
                                        "wrap": True,
                                        "contents": []
                                    }
                                    ]
                                })
                            else:
                                bubble_content["body"]["contents"].insert(lenOfBody, {
                                    "type": "box",
                                    "layout": "baseline",
                                    "contents": [
                                    {
                                        "type": "text",
                                        "text": 'ไม่มีปรากฏชื่อ',
                                        "weight": weight,
                                        "size": size,
                                        "style": "italic",
                                        "flex": 0,
                                        "wrap": True,
                                        "contents": []
                                    }
                                    ]
                                })
                    elif isinstance(data[key], str) and key == 'exhibition_name' and data[key] != 'NONE':
                        # if len(data[key]) > 20:
                        #     data[key] = data[key][:20] + '...'
                        # inset box into contents
                        bubble_content["body"]["contents"].insert(lenOfBody, {
                            "type": "box",
                            "layout": "baseline",
                            "contents": [
                            {
                                "type": "text",
                                "text": data["exhibition_name"],
                                "weight": weight,
                                "size": 'md',
                                "flex": 0,
                                "wrap": True,
                                "contents": []
                            }
                            ]
                        })
                contents.append(bubble_content)
            return carousel
        except Exception as e:
            print('Error: ', e)
            return e

    def reply_images(self, reply_token, image_path):
        try:
            self.line_bot_api.reply_message(
                reply_token,
                ImageSendMessage(
                    original_content_url=image_path, preview_image_url=image_path
                ),
            )
            return "Success"
        except Exception as e:
            return e

    def reply_image(self, reply_token, image_path):
        try:
            self.line_bot_api.reply_message(
                reply_token,
                ImageSendMessage(
                    original_content_url=image_path, preview_image_url=image_path
                ),
            )
            return "Success"
        except Exception as e:
            return e


if __name__ == "__main__":
    ImgSearchBotLine.load_data()
