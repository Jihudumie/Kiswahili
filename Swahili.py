import os
from html import escape

from telegram import (
    Update,
    InputMediaPhoto,
    InputMediaVideo,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)

from deep_translator import GoogleTranslator

# Webhook
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route


# ================= CONFIG =================

BOT_TOKEN = os.getenv("BOT_TOKEN")
URL = os.getenv("URL")
PORT = int(os.getenv("PORT", 10000))

LOG_CHAT_ID = -1002158955567

translator = GoogleTranslator(source="auto", target="sw")


# ================= HELPERS =================

def make_photo(file_id, caption=None):
    return InputMediaPhoto(
        media=file_id,
        caption=caption,
        parse_mode=ParseMode.HTML
    )


def make_video(file_id, caption=None):
    return InputMediaVideo(
        media=file_id,
        caption=caption,
        parse_mode=ParseMode.HTML
    )


# ================= COMMAND =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Karibu!\n"
        "Tuma maandishi, picha, au *album (media group)* — "
        "nitatafsiri kwenda *Kiswahili* pale tu inapohitajika.",
        parse_mode="Markdown"
    )


# ================= MAIN HANDLER =================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message = update.effective_message
        if not message:
            return

        # Media group kwanza
        if message.media_group_id:
            await handle_media_group(update, context)
            return

        if message.text:
            await translate_text(update, context)
            return

        await translate_single_media(update, context)

    except Exception as e:
        await context.bot.send_message(
            LOG_CHAT_ID,
            f"❌ handle_message error:\n{e}"
        )


# ================= TEXT =================

async def translate_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text.startswith("/"):
        return

    translated = translator.translate(text).replace("Mwenyezi Mungu", "Allah")

    # Kama tayari ni Kiswahili
    if translated.strip() == text.strip():
        return

    await update.message.reply_text(translated)


# ================= SINGLE MEDIA =================

async def translate_single_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg.caption:
        return

    translated = translator.translate(msg.caption).replace("Mwenyezi Mungu", "Allah")

    # Skip kama tayari ni Kiswahili
    if translated.strip() == msg.caption.strip():
        return

    if msg.photo:
        await msg.reply_photo(
            msg.photo[-1].file_id,
            caption=translated
        )

    elif msg.video:
        await msg.reply_video(
            msg.video.file_id,
            caption=translated
        )

    elif msg.animation:
        await msg.reply_animation(
            msg.animation.file_id,
            caption=translated
        )


# ================= MEDIA GROUP (JOB QUEUE) =================

async def handle_media_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    group_id = msg.media_group_id

    bot_data = context.application.bot_data
    media_groups = bot_data.setdefault("media_groups", {})
    captions = bot_data.setdefault("media_captions", {})

    # Caption ya kwanza tu
    if group_id not in captions:
        original = msg.caption

        if not original:
            captions[group_id] = None
        else:
            translated = translator.translate(original).replace("Mwenyezi Mungu", "Allah")

            # Kama tayari ni Kiswahili → SKIP group
            if translated.strip() == original.strip():
                captions[group_id] = None
            else:
                captions[group_id] = escape(translated)

    caption = captions[group_id] if len(media_groups.get(group_id, [])) == 0 else None

    if msg.photo:
        media = make_photo(msg.photo[-1].file_id, caption)
    elif msg.video:
        media = make_video(msg.video.file_id, caption)
    else:
        return

    media_groups.setdefault(group_id, []).append(media)

    # Debounce using JobQueue
    for job in context.job_queue.get_jobs_by_name(str(group_id)):
        job.schedule_removal()

    context.job_queue.run_once(
        send_media_group,
        when=1,
        data={"chat_id": msg.chat.id, "group_id": group_id},
        name=str(group_id),
    )


async def send_media_group(context: ContextTypes.DEFAULT_TYPE):
    data = context.job.data
    chat_id = data["chat_id"]
    group_id = data["group_id"]

    bot_data = context.application.bot_data
    media_groups = bot_data.get("media_groups", {})
    captions = bot_data.get("media_captions", {})

    # Kama caption ilikuwa SKIP → usitume chochote
    if captions.get(group_id) is None:
        media_groups.pop(group_id, None)
        captions.pop(group_id, None)
        return

    if group_id in media_groups:
        await context.bot.send_media_group(
            chat_id=chat_id,
            media=media_groups[group_id]
        )

        media_groups.pop(group_id, None)
        captions.pop(group_id, None)


# ================= WEBHOOK =================

async def telegram(request: Request):
    data = await request.json()
    await app.update_queue.put(Update.de_json(data, app.bot))
    return Response()


# ================= MAIN =================

async def main():
    global app
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(
            filters.ALL & (
                filters.ChatType.PRIVATE |
                filters.ChatType.GROUP |
                filters.ChatType.SUPERGROUP
            ),
            handle_message
        )
    )

    starlette_app = Starlette(
        routes=[Route("/telegram", telegram, methods=["POST"])]
    )

    server = uvicorn.Server(
        uvicorn.Config(
            app=starlette_app,
            host="0.0.0.0",
            port=PORT,
            log_level="info"
        )
    )

    await app.bot.set_webhook(f"{URL}/telegram")

    async with app:
        await app.start()
        await server.serve()
        await app.stop()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
