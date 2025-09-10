import os
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from PIL import Image
import io
from telegram import InputMediaPhoto, InputMediaVideo, InputMediaDocument

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome! Send /setthumb to upload a new thumbnail, /viewthumb to see current thumbnail, or /delthumb to delete it. Send any file to apply the thumbnail."
    )

async def set_thumbnail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please send the image to set as thumbnail.")
    context.user_data["awaiting_thumbnail"] = True

async def view_thumbnail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "thumbnail" in context.user_data:
        await update.message.reply_photo(
            photo=context.user_data["thumbnail"],
            caption="Current thumbnail"
        )
    else:
        await update.message.reply_text("No thumbnail set yet.")

async def delete_thumbnail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "thumbnail" in context.user_data:
        del context.user_data["thumbnail"]
        await update.message.reply_text("Thumbnail deleted.")
    else:
        await update.message.reply_text("No thumbnail to delete.")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_thumbnail"):
        if update.message.photo:
            photo = update.message.photo[-1]
            file = await photo.get_file()
            file_bytes = await file.download_as_bytearray()
            
            # Verify and process image
            try:
                img = Image.open(io.BytesIO(file_bytes))
                img.verify()  # Verify it's a valid image
                context.user_data["thumbnail"] = file_bytes
                context.user_data["awaiting_thumbnail"] = False
                await update.message.reply_text("Thumbnail set successfully!")
            except Exception as e:
                await update.message.reply_text(f"Error setting thumbnail: {str(e)}")
        else:
            await update.message.reply_text("Please send a valid image for thumbnail.")
        return

    # Handle files (video/document)
    if update.message.video or update.message.document:
        if "thumbnail" not in context.user_data:
            await update.message.reply_text("Please set a thumbnail first using /setthumb")
            return

        file = update.message.video or update.message.document
        file_name = getattr(file, "file_name", "file")
        
        try:
            # Send file with custom thumbnail
            if update.message.video:
                await update.message.reply_video(
                    video=file,
                    thumb=context.user_data["thumbnail"],
                    caption=f"File with custom thumbnail: {file_name}"
                )
            else:
                await update.message.reply_document(
                    document=file,
                    thumb=context.user_data["thumbnail"],
                    caption=f"File with custom thumbnail: {file_name}"
                )
            await update.message.reply_text("File sent with custom thumbnail!")
        except Exception as e:
            await update.message.reply_text(f"Error applying thumbnail: {str(e)}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.message:
        await update.message.reply_text("An error occurred. Please try again.")

def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN not set in environment variables")

    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("setthumb", set_thumbnail))
    application.add_handler(CommandHandler("viewthumb", view_thumbnail))
    application.add_handler(CommandHandler("delthumb", delete_thumbnail))
    application.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.ALL, handle_file))
    application.add_error_handler(error_handler)

    # Start the bot with webhook for Render
    port = int(os.environ.get("PORT", 8443))
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=BOT_TOKEN,
        webhook_url=f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{BOT_TOKEN}"
    )

if __name__ == "__main__":
    main()
