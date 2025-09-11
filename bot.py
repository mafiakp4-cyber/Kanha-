import os
import threading
from pyrogram import Client, filters
from flask import Flask
from PIL import Image

# 🔑 Config
API_ID = int(os.environ.get("API_ID", "21302239"))
API_HASH = os.environ.get("API_HASH", "1560930c983fbca6a1fcc8eab760d40d")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8134357026:AAHxf3ncIOk9J4iNg2UHQ7cxeIlcQfnmLfU")

# Pyrogram Client
app = Client(
    "ThumbChangerBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ✅ User thumbnail store
user_thumbs = {}

# Function to resize & compress image to ≤2MB JPG
def process_thumbnail(input_path, output_path):
    img = Image.open(input_path).convert("RGB")

    # Resize if too big (max 1280px width/height for Telegram thumbs)
    img.thumbnail((1280, 1280))

    # Save with compression until size ≤ 2MB
    quality = 95
    while True:
        img.save(output_path, "JPEG", quality=quality)
        if os.path.getsize(output_path) <= 2 * 1024 * 1024:  # 2MB
            break
        quality -= 5
        if quality < 20:
            break  # stop if quality too low


# Step 1: Save user thumbnail
@app.on_message(filters.photo & filters.private)
async def save_thumb(client, message):
    user_id = message.from_user.id
    raw_path = f"{user_id}_raw.jpg"
    final_path = f"{user_id}_thumb.jpg"

    # Download original image
    await client.download_media(message.photo.file_id, file_name=raw_path)

    # Resize & compress to ≤2MB
    process_thumbnail(raw_path, final_path)
    user_thumbs[user_id] = final_path

    os.remove(raw_path)  # remove raw file
    await message.reply_text("✅ Thumbnail सेव हो गया!\nअब कोई MP4 video भेजो।")


# Step 2: Send video with new thumbnail
@app.on_message(filters.video & filters.private)
async def send_with_thumb(client, message):
    user_id = message.from_user.id
    if user_id not in user_thumbs:
        return await message.reply_text("❌ पहले कोई thumbnail photo भेजो।")

    thumb_path = user_thumbs[user_id]

    # Show processing
    status = await message.reply_text("⏳ Processing...")

    try:
        await client.send_video(
            chat_id=message.chat.id,
            video=message.video.file_id,
            thumb=thumb_path,
            caption="✅ Done! Thumbnail changed."
        )
        await status.edit_text("✅ Thumbnail successfully changed!")
    except Exception as e:
        await status.edit_text(f"❌ Error: {e}")


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
