from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage, ImageSendMessage, FlexSendMessage

#  pip install line-bot-sdk
from linebot import LineBotSdkDeprecatedIn30
import warnings

from dotenv import load_dotenv
import os

class ImgSearchBotLine:
    def __init__(self, channel_access_token, channel_secret):
        # Suppress warning messages
        warnings.filterwarnings("ignore", category=LineBotSdkDeprecatedIn30)
        self.line_bot_api = LineBotApi(channel_access_token)
        self.handler = WebhookHandler(channel_secret)

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

    def push_flex(self, user_id, flex):
        try:
            self.line_bot_api.push_message(user_id, FlexSendMessage(alt_text="hello", contents=flex))
            return "Success"
        except Exception as e:
            return e

    def create_carousel(response):
        try:
            contents = []
            carousel = {"type": "carousel", "contents": contents}
            for data in response:
                if 'http' in data["image_url"]:
                    url = data["image_url"].split("/")[-1]
                else:
                    url = data["image_url"]
                # get env
                load_dotenv('./.env')
                ip = os.getenv("IP_URL")+'imgsearch/'
                url = ip + url
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
                        "uri": data["url"]
                        }
                    },
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "sm",
                        "contents": [
                        {
                            "type": "text",
                            "text": data["artwork_name"],
                            "weight": "bold",
                            "size": "lg",
                            "align": "center",  
                            "wrap": True,
                            "contents": []
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "contents": [
                            {
                                "type": "text",
                                "text": data["artist_name"],
                                "weight": "regular",
                                "size": "md",
                                "flex": 0,
                                "wrap": True,
                                "contents": []
                            }
                            ]
                        }
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
                contents.append(bubble_content)
            return carousel
        except Exception as e:
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
