from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import re

app = Flask(__name__)
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except Exception as e:
        print("Error:", e)
        abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    reply = calculate_rotation_rate(text)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

def calculate_rotation_rate(text):
    lend_rate = 250  # 貸玉レート固定

    # 通常回転数を抽出
    rotation_match = re.search(r"(通常)?\s*(\d{1,4})\s*回転", text)
    rotation = int(rotation_match.group(2)) if rotation_match else None

    # 使用玉数を抽出
    usage_match = re.search(r"(使用|投資)?\s*(\d{3,5})\s*玉", text)
    used_balls = int(usage_match.group(2)) if usage_match else None

    if rotation is None or used_balls is None:
        return "『使用玉数』と『通常回転数』を含めた入力をしてください（例：使用1625玉 通常140回転）"

    used_yen = used_balls / lend_rate * 1000
    rate = round(rotation / used_yen * 1000, 2)

    return (
        f"回転率：{rate} 回転/千円\n"
        f"（回転数: {rotation}、使用玉数: {used_balls}玉、貸玉レート: {lend_rate}玉/1000円）"
    )

if __name__ == "__main__":
    app.run()
