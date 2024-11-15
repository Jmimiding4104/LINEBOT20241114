
from flask import Flask, request
import json
import re
#from linebot import LineBotApi, WebhookHandler
#from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, ButtonsTemplate, PostbackAction

from linebot.v3 import WebhookHandler
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent

app = Flask(__name__)

user_info = {
    "name": None,
    "idNumber": None,
    "tel": None,
    "step": 0  # 用來追蹤步驟，0 表示尚未開始，1 表示請輸入姓名，2 表示請輸入身分證字號，以此類推
}


def send_operation_options(line_bot_api, reply_token):
    buttons_template = ButtonsTemplate(
        title="請問你要進行什麼操作？",
        text="請點擊以下選項",
        actions=[
            PostbackAction(label="開始集點", data="start"),
            PostbackAction(label="不需要操作", data="finish")
        ]
    )
    template_message = TemplateSendMessage(
        alt_text="請問你要進行什麼操作？",
        template=buttons_template
    )
    line_bot_api.reply_message(reply_token, template_message)
    
def send_other_operation_options(line_bot_api, reply_token):
    buttons_template = ButtonsTemplate(
        title="請問你還需要處理其他項目嗎？",
        text="請點擊以下選項",
        actions=[
            PostbackAction(label="生理監測", data="monitor"),
            PostbackAction(label="AI衛教", data="educate"),
            PostbackAction(label="運動", data="exercise"),
            PostbackAction(label="登出", data="logout")
        ]
    )
    template_message = TemplateSendMessage(
        alt_text="請問你還需要處理其他項目嗎？",
        template=buttons_template
    )
    line_bot_api.reply_message(reply_token, template_message)


@app.route("/", methods=['POST'])
def linebot():
    global user_info
    body = request.get_data(as_text=True)
    try:
        json_data = json.loads(body)
        access_token = 'mh/r45bGW1j8Nvk2G/X8/1j+jf/0H60retZSLmLZ2bCJtwuMRB308Vnk5/LHQ4Yk2uGR/rkCQYoUvnqOl20BHaR8LmQTCWy4kldRqfUn5rBqRIQxUA171It7o+mRHPJHfU7H/v8H9ZZRQ0b/pxEmuQdB04t89/1O/w1cDnyilFU='
        secret = '84d36b609616d351c7c3cba259f0b769'
        line_bot_api = Configuration(access_token=access_token)
        handler = WebhookHandler(secret)
        signature = request.headers['X-Line-Signature']
        handler.handle(body, signature)

        event = json_data['events'][0]
        if event['type'] == 'message' and event['message']['type'] == 'text':
            msg = event['message']['text']
            tk = event['replyToken']
            user_id = event['source']['userId'] 

            if msg == "新會員":
                user_info["step"] = 1
                line_bot_api.reply_message(tk, TextSendMessage(text="請輸入姓名"))
            elif user_info["step"] == 1:
                user_info["name"] = msg
                user_info["step"] = 2
                line_bot_api.reply_message(
                    tk, TextSendMessage(text="請輸入身分證字號"))
            elif user_info["step"] == 2:
                user_info["idNumber"] = msg
                user_info["step"] = 3
                line_bot_api.reply_message(tk, TextSendMessage(text="請輸入電話"))
            elif user_info["step"] == 3:
                user_info["tel"] = msg
                user_info["step"] = 4  # 重置步驟以便完成註冊
                # 回覆完成訊息

                buttons_template = ButtonsTemplate(
                    title=f"您的姓名是 {user_info['name']}、身份證字號是{
                        user_info['idNumber']}、電話是{user_info['tel']}?",
                    text="請問是否正確",
                    actions=[
                        PostbackAction(label="是", data="correct"),
                        PostbackAction(label="否", data="incorrect")
                    ]
                )

                template_message = TemplateSendMessage(
                    alt_text="確認姓名",
                    template=buttons_template
                )
                line_bot_api.reply_message(tk, template_message)

            elif re.match(r'^[A-Za-z]\d{9}$', msg) or user_info["step"] == 4:
                send_operation_options(line_bot_api, tk)

        if event['type'] == 'postback':
            tk = event['replyToken']
            data = event['postback']['data']

            if data == "correct":
                line_bot_api.reply_message(
                    tk, TextSendMessage(text="請輸入會員身分證字號"))
            elif data == "incorrect":
                user_info = {  # 重設 user_info
                    "name": "",
                    "idNumber": "",
                    "tel": "",
                    "step": 1
                }
                line_bot_api.reply_message(tk, TextSendMessage(text="請輸入姓名"))
            elif data == "start":
                buttons_template = ButtonsTemplate(
                    title="請問你要處理哪個項目？",
                    text="請點擊以下選項",
                    actions=[
                        PostbackAction(label="生理監測", data="monitor"),
                        PostbackAction(label="AI衛教", data="educate"),
                        PostbackAction(label="運動", data="exercise"),
                        PostbackAction(label="登出", data="logout")
                    ]
                )
                template_message = TemplateSendMessage(
                    alt_text="請問你要進行什麼集點？",
                    template=buttons_template
                )
                line_bot_api.reply_message(tk, template_message)
            elif data == "finish":
                user_info = {  # 重設 user_info
                    "name": "",
                    "idNumber": "",
                    "tel": "",
                    "step": 0
                }
            elif data == "monitor":
                send_other_operation_options(line_bot_api, tk)
            elif data == "educate":
                send_other_operation_options(line_bot_api, tk)
            elif data == "exercise":
                send_other_operation_options(line_bot_api, tk)
            elif data == "logout":
                user_info = {  # 重設 user_info
                    "name": "",
                    "idNumber": "",
                    "tel": "",
                    "step": 0
                }
            line_bot_api.reply_message(tk, TextSendMessage(text="請重新登入"))

    except Exception as e:
        print(f"Error: {e}")

    return 'OK'


if __name__ == "__main__":
    app.run()

# ngrok http http://127.0.0.1:5000
