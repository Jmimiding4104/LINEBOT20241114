from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    TemplateMessage,
    ButtonsTemplate,
    PostbackAction
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent, PostbackEvent

app = Flask(__name__)

user_info = {
    "name": None,
    "idNumber": None,
    "tel": None,
    "step": 0  # 用來追蹤步驟，0 表示尚未開始，1 表示請輸入姓名，2 表示請輸入身分證字號，以此類推
}

configuration = Configuration(
    access_token='mh/r45bGW1j8Nvk2G/X8/1j+jf/0H60retZSLmLZ2bCJtwuMRB308Vnk5/LHQ4Yk2uGR/rkCQYoUvnqOl20BHaR8LmQTCWy4kldRqfUn5rBqRIQxUA171It7o+mRHPJHfU7H/v8H9ZZRQ0b/pxEmuQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('84d36b609616d351c7c3cba259f0b769')


@app.route("/", methods=['POST'])
def linebot():
    global user_info

    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        tk = event.reply_token

        if event.message.text == "新會員":
            user_info["step"] = 1
            reply_text = "請輸入姓名"
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=tk,
                    messages=[TextMessage(text=reply_text)]
                )
            )
        elif user_info["step"] == 1:
            user_info["name"] = event.message.text
            user_info["step"] = 2
            reply_text = "請輸入身分證字號"
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=tk,
                    messages=[TextMessage(text=reply_text)]
                )
            )
        elif user_info["step"] == 2:
            user_info["idNumber"] = event.message.text
            user_info["step"] = 3
            reply_text = "請輸入電話號碼"
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=tk,
                    messages=[TextMessage(text=reply_text)]
                )
            )
        elif user_info["step"] == 3:
            user_info["tel"] = event.message.text
            user_info["step"] = 4

            # Create confirmation template message
            buttons_template = ButtonsTemplate(
                title="請確認您的資料",
                text=(
                    f"您的姓名是 {user_info['name']}、\n"
                    f"身份證字號是 {user_info['idNumber']}、\n"
                    f"電話是 {user_info['tel']}。\n請問是否正確？"
                ),
                actions=[
                    PostbackAction(label="是", data="correct"),
                    PostbackAction(label="否", data="incorrect")
                ]
            )

            template_message = TemplateMessage(
                alt_text="確認資料",
                template=buttons_template
            )

            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=tk,
                    messages=[template_message]
                )
            )


@handler.add(PostbackEvent)
def handle_postback(event):
    global user_info
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        
        tk = event.reply_token
        data = event.postback.data
        
        if data == "correct":
            # Confirm registration completion
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=tk,
                    messages=[TextMessage(text="感謝註冊！")]
                )
            )
        elif data == "incorrect":
            # Reset user information if incorrect
            user_info = {
                "name": None,
                "idNumber": None,
                "tel": None,
                "step": 0
            }
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=tk,
                    messages=[TextMessage(text="請重新輸入姓名")]
                )
            )

if __name__ == "__main__":
    app.run()

# ngrok http http://127.0.0.1:5000
