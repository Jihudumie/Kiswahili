from html import escape
from telegram import Update
from telegram.ext import ContextTypes
from services.translator import translator_service
from utils.media_helpers import make_photo, make_video
from config import MEDIA_GROUP_DEBOUNCE_SECONDS, LOG_CHAT_ID


async def translate_single_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle single photo/video with caption"""
    msg = update.message

    if not msg.caption:
        return

    # Translate caption
    translated = translator_service.translate(msg.caption)

    if not translator_service.should_translate(msg.caption, translated):
        return

    # Reply with appropriate media type
    if msg.photo:
        await msg.reply_photo(
            msg.photo[-1].file_id,
            caption=translated,
            message_thread_id=msg.message_thread_id
        )

    elif msg.video:
        await msg.reply_video(
            msg.video.file_id,
            caption=translated,
            message_thread_id=msg.message_thread_id
        )

    elif msg.animation:
        await msg.reply_animation(
            msg.animation.file_id,
            caption=translated,
            message_thread_id=msg.message_thread_id
        )
        
    elif msg.document:
        await msg.reply_document(
            msg.document.file_id,
            caption=translated,
            message_thread_id=msg.message_thread_id
        )
        
    elif msg.audio:
        await msg.reply_audio(
            msg.audio.file_id,
            caption=translated,
            message_thread_id=msg.message_thread_id
        )


# ==== MEDIA GROUP (JOB QUEUE) =================

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

    # Debounce JobQueue
    for job in context.job_queue.get_jobs_by_name(str(group_id)):
        job.schedule_removal()

    context.job_queue.run_once(
        send_media_group,
        when=1,
        data={
            "chat_id": msg.chat.id,
            "group_id": group_id,
            "thread_id": msg.message_thread_id,  # 🔑 topic support
        },
        name=str(group_id),
    )


async def send_media_group(context: ContextTypes.DEFAULT_TYPE):
    data = context.job.data
    chat_id = data["chat_id"]
    group_id = data["group_id"]
    thread_id = data.get("thread_id")

    bot_data = context.application.bot_data
    media_groups = bot_data.get("media_groups", {})
    captions = bot_data.get("media_captions", {})

    # Kama caption ilikuwa SKIP
    if captions.get(group_id) is None:
        media_groups.pop(group_id, None)
        captions.pop(group_id, None)
        return

    if group_id in media_groups:
        await context.bot.send_media_group(
            chat_id=chat_id,
            media=media_groups[group_id],
            message_thread_id=thread_id
        )

        media_groups.pop(group_id, None)
        captions.pop(group_id, None)





