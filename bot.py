import os
import threading
from pyrogram import Client, filters
from flask import Flask

# ----------------- Config -----------------
API_ID = int(os.environ.get("API_ID", "21302239"))
API_HASH = os.environ.get("API_HASH", "1560930c983fbca6a1fcc8eab760d40d")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8134357026:AAHxf3ncIOk9J4iNg2UHQ7cxeIlcQfnmLfU")

# ----------------- Pyrogram Client -----------------
app = Client(
    "ThumbChangerBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ----------------- User Thumbnail Store -----------------
user_thumbs = {}

# ----------------- Step 1: Save Thumbnail -----------------
@app.on_message(filters.photo & filters.private)
async def save_thumb(client, message):
    user_id = message.from_user.id
    thumb_path = await client.download_media(message.photo.file_id)
    user_thumbs[user_id] = thumb_path
    await message.reply_text("✅ Thumbnail saved! अब कोई video भेजो।")

# ----------------- Step 2: Send Video with Thumbnail -----------------
@app.on_message(filters.video & filters.private)
async def send_with_thumb(client, message):
    user_id = message.from_user.id
    if user_id not in user_thumbs:
        return await message.reply_text("❌ पहले कोई thumbnail भेजो।")

    thumb_path = user_thumbs[user_id]

    status = await message.reply_text("⏳ Processing...")

    await client.send_video(
        chat_id=message.chat.id,
        video=message.video.file_id,
        thumb=thumb_path,
        caption="✅ Thumbnail changed successfully!"
    )

    await status.edit_text("✅ Done! Thumbnail updated!")

# ----------------- Flask for Render -----------------
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "✅ Thumbnail Bot is running on Render!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)

# ----------------- Run both -----------------
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    app.run()
