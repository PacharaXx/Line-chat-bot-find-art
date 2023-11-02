import json
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage, ImageSendMessage, FlexSendMessage
#  pip install line-bot-sdk
from sentence_transformers import util
from linebot import LineBotSdkDeprecatedIn30
import warnings


class ImgSearchBotLine():

    def __init__(self, channel_access_token, channel_secret):
        # Suppress warning messages
        warnings.filterwarnings("ignore", category=LineBotSdkDeprecatedIn30)
        self.line_bot_api = LineBotApi(channel_access_token)
        self.handler = WebhookHandler(channel_secret)

    def reply(self, reply_token, message):
        try:
            self.line_bot_api.reply_message(
                reply_token, TextSendMessage(text=message))
            return 'Success'
        except Exception as e:
            return e

    def push(self, user_id, message):
        try:
            self.line_bot_api.push_message(
                user_id, TextSendMessage(text=message))
            return 'Success'
        except Exception as e:
            return e

    def push_image(self, user_id, image_path):
        try:
            self.line_bot_api.push_message(user_id, ImageSendMessage(
                original_content_url=image_path, preview_image_url=image_path))
            return 'Success'
        except Exception as e:
            return e

    def push_flex(self, user_id, flex):
        try:
            self.line_bot_api.push_message(
                user_id, FlexSendMessage(alt_text="hello", contents=flex))
            return 'Success'
        except Exception as e:
            return e

    def create_carousel(image_paths):
        contents = []
        carousel = {
        "type": "carousel",
        "contents": contents
        }
        for image_path in image_paths:
            contents.append({
                "type": "bubble",
                "hero": {
                    "type": "image",
                    "url": image_path,
                    "size": "full",
                    "aspectRatio": "20:13",
                    "aspectMode": "cover",
                    "action": {
                        "type": "uri",
                        "uri": "https://example.com"  # Replace with the appropriate URI
                    }
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "Brown Cafe",
                            "weight": "bold",
                            "size": "xl"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "margin": "lg",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "baseline",
                                    "spacing": "sm",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "Place",
                                            "color": "#aaaaaa",
                                            "size": "sm",
                                            "flex": 1
                                        },
                                        {
                                            "type": "text",
                                            "text": "Miraina Tower, 4-1-6 Shinjuku, Tokyo",
                                            "wrap": True,
                                            "color": "#666666",
                                            "size": "sm",
                                            "flex": 5
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "baseline",
                                    "spacing": "sm",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "Time",
                                            "color": "#aaaaaa",
                                            "size": "sm",
                                            "flex": 1
                                        },
                                        {
                                            "type": "text",
                                            "text": "10:00 - 23:00",
                                            "wrap": True,
                                            "color": "#666666",
                                            "size": "sm",
                                            "flex": 5
                                        }
                                    ]
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
                            "style": "link",
                            "height": "sm",
                            "action": {
                                "type": "uri",
                                "label": "รายละเอียดเพิ่มเติม",  # Replace with your label
                                "uri": "https://example.com"  # Replace with the appropriate URI
                            }
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [],
                            "margin": "sm"
                        }
                    ],
                    "flex": 0
                }
            })
        return json.dumps(carousel, indent=2)

    def reply_images(self, reply_token, image_path):
        try:
            self.line_bot_api.reply_message(reply_token, ImageSendMessage(
                original_content_url=image_path, preview_image_url=image_path))
            return 'Success'
        except Exception as e:
            return e

    def reply_image(self, reply_token, image_path):
        try:
            self.line_bot_api.reply_message(reply_token, ImageSendMessage(
                original_content_url=image_path, preview_image_url=image_path))
            return 'Success'
        except Exception as e:
            return e


if __name__ == '__main__':
    ImgSearchBotLine.load_data()
