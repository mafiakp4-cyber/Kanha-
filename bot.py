import os
import threading
from pyrogram import Client, filters
from flask import Flask

# 🔑 Config
API_ID = int(os.environ.get("API_ID", "21302239"))        # my.telegram.org से
API_HASH = os.environ.get("API_HASH", "1560930c983fbca6a1fcc8eab760d40d")  # my.telegram.org से
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8134357026:AAHxf3ncIOk9J4iNg2UHQ7cxeIlcQfnmLfU")  # BotFather से

# Pyrogram Client
app = Client(
    "ThumbChangerBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ✅ User thumbnail store
user_thumbs = {}

# Step 1: Thumbnail Save
@app.on_message(filters.photo & filters.private)
async def save_thumb(client, message):
    user_id = message.from_user.id
    photo = message.photo.file_id

    thumb_path = await client.download_media(photo, file_name=f"{user_id}.jpg")
    user_thumbs[user_id] = thumb_path

    await message.reply_text("✅ Thumbnail सेव हो गया!\nअब कोई MP4 video भेजो।")

# Step 2: Video with new Thumbnail
@app.on_message(filters.video & filters.private)
async def send_with_thumb(client, message):
    user_id = message.from_user.id
    if user_id not in user_thumbs:
        return await message.reply_text("❌ पहले कोई thumbnail photo भेजो।")

    thumb_path = user_thumbs[user_id]

    # Processing message
    status = await message.reply_text("⏳ Processing...")

    # Send video with custom thumbnail
    await client.send_video(
        chat_id=message.chat.id,
        video=message.video.file_id,
        thumb=thumb_path,
        caption="✅ Done! Thumbnail changed."
    )

    await status.edit_text("✅ Thumbnail successfully changed!")

# ==================== Flask for Render ====================
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "✅ Thumbnail Bot is running on Render!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)

# ==================== Run both ====================
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    app.run()
