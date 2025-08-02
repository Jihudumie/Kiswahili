import os
import asyncio
from telegram.ext import Application, MessageHandler, ContextTypes, filters
from telegram import Update, InputMediaPhoto, InputMediaVideo, InputMediaAudio
from telegram.ext import Updater, ContextTypes
from deep_translator import GoogleTranslator


#WebHook
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

BOT_TOKEN = os.getenv("BOT_TOKEN")
URL = os.getenv("URL")

PORT = int(os.environ.get("PORT", 10000))

# Kutafsiri ujumbe kwenda Kiswahili
translator = GoogleTranslator(source='auto', target='sw')


async def update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        message = update.message

        if not message:
            return

        if message.text:
            await tr_text(update, context)
        else:
            await tr_picha_video(update, context)

    except Exception as e:
        error_msg = f"Kuna hitilafu kwenye function kuu ya `update`: {str(e)}"
        await context.bot.send_message(chat_id=-1002158955567, text=error_msg)
        
        


# Tafsiri ujumbe wa maandishi
async def tr_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        message = update.message.text

        if message.startswith('/'):
            return

        translation_text = translator.translate(message).replace("Mwenyezi Mungu", "Allah")

        if message == translation_text:
            return

        asyncio.create_task(update.message.reply_text(translation_text, disable_web_page_preview=True))
        return 

    except Exception as e:
        error_msg = f"Kuna hitilafu imejitokeza kwenye function ya Tafsiri ujumbe wa maandishi: {str(e)}"
        asyncio.create_task(context.bot.send_message(chat_id=-1002158955567, text=error_msg))


# Tafsiri picha au video na tuma
async def tr_picha_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        caption = update.message.caption

        if not caption:
            return

        translation_text = translator.translate(caption).replace("Mwenyezi Mungu", "Allah")

        if caption == translation_text:
            return

        elif update.message.photo:
            for photo in update.message.photo:
                asyncio.create_task(update.message.reply_photo(photo=photo.file_id, caption=translation_text))
                return 

        elif update.message.video:
            asyncio.create_task(update.message.reply_video(video=update.message.video.file_id, caption=translation_text))
            return 

        elif update.message.animation:
            asyncio.create_task(update.message.reply_animation(animation=update.message.animation.file_id, caption=translation_text))
            return 

    except Exception as e:
        error_msg = f"Kuna hitilafu imejitokeza kwenye function ya Tafsiri picha/video: {str(e)}"
        asyncio.create_task(context.bot.send_message(chat_id=-1002158955567, text=error_msg))


                    


async def telegram(request: Request) -> Response:
    """Shughulikia webhook requests kutoka Telegram"""
    data = await request.json()
    await app.update_queue.put(Update.de_json(data=data, bot=app.bot))
    return Response()


async def main():
    global app  # ili itumike ndani ya `telegram()`
    app = Application.builder().token(BOT_TOKEN).build()

    # Ruhusu PRIVATE na MAGROUP (GROUP + SUPERGROUP)
    app.add_handler(
        MessageHandler(
            filters.ALL & (
                filters.ChatType.PRIVATE |
                filters.ChatType.GROUP |
                filters.ChatType.SUPERGROUP
            ),
            update
        )
    )

    # Tengeneza Starlette app
    starlette_app = Starlette(
        routes=[
            Route("/telegram", telegram, methods=["POST"]),
        ]
    )

    # Tengeneza uvicorn server
    webserver = uvicorn.Server(
        config=uvicorn.Config(
            app=starlette_app,
            host="0.0.0.0",
            port=PORT,
            log_level="info"
        )
    )

    # Weka webhook
    await app.bot.set_webhook(url=f"{URL}/telegram")

    # Anzisha bot na webserver
    async with app:
        await app.start()
        await webserver.serve()
        await app.stop()


if __name__ == "__main__":
    asyncio.run(main())





