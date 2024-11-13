from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# 使用您的 Channel Access Token 和 Channel Secret
line_bot_api = LineBotApi('2006566438')
handler = WebhookHandler('84d36b609616d351c7c3cba259f0b769')

@app.route("/callback", methods=['POST'])
def callback():
    # 驗證請求是否來自 LINE
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    return 'OK'

# 設置處理訊息的回調函數
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 回傳相同的訊息給用戶
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text)
    )

if __name__ == "__main__":
    app.run()
