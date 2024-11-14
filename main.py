
from flask import Flask, request
import json, re
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, PostbackEvent, TemplateSendMessage, ButtonsTemplate, PostbackAction

app = Flask(__name__)

user_info = {
    "name": None,
    "idNumber": None,
    "tel": None,
    "step": 0  # 用來追蹤步驟，0 表示尚未開始，1 表示請輸入姓名，2 表示請輸入身分證字號，以此類推
}


@app.route("/", methods=['POST'])
def linebot():
    global user_info
    body = request.get_data(as_text=True)
    try:
        json_data = json.loads(body)
        access_token = 'mh/r45bGW1j8Nvk2G/X8/1j+jf/0H60retZSLmLZ2bCJtwuMRB308Vnk5/LHQ4Yk2uGR/rkCQYoUvnqOl20BHaR8LmQTCWy4kldRqfUn5rBqRIQxUA171It7o+mRHPJHfU7H/v8H9ZZRQ0b/pxEmuQdB04t89/1O/w1cDnyilFU='
        secret = '84d36b609616d351c7c3cba259f0b769'
        line_bot_api = LineBotApi(access_token)
        handler = WebhookHandler(secret)
        signature = request.headers['X-Line-Signature']
        handler.handle(body, signature)

        event = json_data['events'][0]
        if event['type'] == 'message' and event['message']['type'] == 'text':
            msg = event['message']['text']
            tk = event['replyToken']

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
                    title=f"您的姓名是 {user_info['name']}、身份證字號是{user_info['idNumber']}、電話是{user_info['tel']}?",
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
                line_bot_api.reply_message(tk, TextSendMessage(text="4648646"))

        if event['type'] == 'postback':
            tk = event['replyToken']
            data = event['postback']['data']
            
            if data == "correct":
                line_bot_api.reply_message(tk, TextSendMessage(text="感謝註冊！"))
            elif data == "incorrect":
                user_info = {  # 重設 user_info
            "name": "",
            "idNumber": "",
            "tel": "",
            "step": 0
            }
            line_bot_api.reply_message(tk, TextSendMessage(text="請重新輸入姓名"))

    except Exception as e:
        print(f"Error: {e}")
        print(body)

    return 'OK'


if __name__ == "__main__":
    app.run()
