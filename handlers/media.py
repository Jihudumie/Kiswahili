async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main message router"""
    try:
        message = update.effective_message
        if not message:
            return

        # Media group (album)
        if message.media_group_id:
            await handle_media_group(update, context)
            return

        # Maandishi
        if message.text:
            from handlers.text import translate_text
            await translate_text(update, context)
            return

        # Voice (shughulikiwa tu kama ina caption)
        if message.voice and message.caption:
            await translate_single_media(update, context)
            return

        # Audio (shughulikiwa tu kama ina caption)
        if message.audio and message.caption:
            await translate_single_media(update, context)
            return

        # Document (shughulikiwa tu kama ina caption)
        if message.document and message.caption:
            await translate_single_media(update, context)
            return

        # Photo / Video / Animation (tayari zina logic ya caption ndani)
        await translate_single_media(update, context)

    except Exception as e:
        await context.bot.send_message(
            LOG_CHAT_ID,
            f"❌ handle_message error:\n{e}"
        )
