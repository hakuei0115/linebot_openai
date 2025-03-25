from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os

app = Flask(__name__)

openai.api_key = os.getenv('OPENAI_API_KEY')
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler1 = WebhookHandler(os.getenv('CHANNEL_SECRET'))

counter = 0

@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler1.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler1.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global counter
    text1 = event.message.text
    try:
        response = openai.ChatCompletion.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是一位有趣又資深的全端工程師，擅長用淺顯易懂的方式教初學者前後端技術，"
                        "請用繁體中文回答使用者的問題。"
                    )
                },
                {"role": "user", "content": text1}
            ]
            model="gpt-4o-mini-2024-07-18",
            temperature=0.5,
        )
        ret = response['choices'][0]['message']['content'].strip()
        counter += 1
    except:
        ret = '發生錯誤！'

    line_bot_api.reply_message(event.reply_token, [
        TextSendMessage(text=ret),
        TextSendMessage(text=f"共傳了 {counter} 則訊息。")
    ])

if __name__ == '__main__':
    app.run()
