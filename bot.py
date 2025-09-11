import os
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = int(os.environ.get("API_ID", 21302239))
API_HASH = os.environ.get("API_HASH", "1560930c983fbca6a1fcc8eab760d40d")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8134357026:AAHxf3ncIOk9J4iNg2UHQ7cxeIlcQfnmLfU")

app = Client("thumb_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# user wise thumbnail store
user_thumbs = {}

# जब user कोई photo भेजे → thumbnail save
@app.on_message(filters.photo & filters.private)
async def save_thumb(client, message: Message):
    user_id = message.from_user.id
    thumb_path = f"downloads/{user_id}_thumb.jpg"
    os.makedirs("downloads", exist_ok=True)
    await message.download(file_name=thumb_path)
    user_thumbs[user_id] = thumb_path
    await message.reply_text("✅ Thumbnail saved successfully!")

# जब user कोई video/file भेजे
@app.on_message(filters.video | filters.document)
async def send_with_thumb(client, message: Message):
    user_id = message.from_user.id
    if user_id not in user_thumbs:
        await message.reply_text("❌ पहले कोई thumbnail photo भेजो।")
        return
    
    thumb = user_thumbs[user_id]
    file = message.video or message.document
    file_name = file.file_name
    
    await message.reply_text("⏳ Processing thumbnail...")
    await client.send_video(
        chat_id=message.chat.id,
        video=file.file_id,
        thumb=thumb,
        caption=f"🎬 {file_name}\n✅ Thumbnail changed!"
    )

print("🚀 Bot started...")
app.run()
