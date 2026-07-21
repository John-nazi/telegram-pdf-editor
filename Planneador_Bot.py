import logging
import os

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ============================================================
# CONFIGURACIÓN
# ============================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PORT = int(os.getenv("PORT", "10000"))
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")

WEBAPP_URL = "https://john-nazi.github.io/telegram-pdf-editor/"

LINK_SEMANA_30 = (
    "https://grupometalsa.sharepoint.com/_layouts/15/"
    "sharepoint.aspx/onedrive"
)

LINK_SEMANA_29 = (
    "https://grupometalsa.sharepoint.com/:f:/s/"
    "PLANEACINPINTURA-SECUENCIADO/"
    "IgDvLH9YaYYMTo3p3VzuSQm9AZRCg2UsNNgMG_LRiza_K5c"
)

LINK_SEMANA_28 = (
    "https://grupometalsa.sharepoint.com/:f:/s/"
    "PLANEACINPINTURA-SECUENCIADO/"
    "IgAeUsb_6TNgTJfF9LsZ_c8pAc_WP26JO_u4Nvm6uUz5Kjs"
)


# ============================================================
# COMANDO /START
# ============================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    if update.message is None:
        return

    await update.message.reply_text(
        "Bot activo.\n\n"
        "Usa /semanas para consultar las carpetas "
        "o envía un archivo PDF."
    )


# ============================================================
# COMANDO /SEMANAS
# ============================================================

async def mostrar_semanas(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    if update.message is None:
        return

    botones = [
        [
            InlineKeyboardButton(
                text="📁 SEMANA 30",
                url=LINK_SEMANA_30,
            )
        ],
        [
            InlineKeyboardButton(
                text="📁 SEMANA 29",
                url=LINK_SEMANA_29,
            )
        ],
        [
            InlineKeyboardButton(
                text="📁 SEMANA 28",
                url=LINK_SEMANA_28,
            )
        ],
    ]

    teclado = InlineKeyboardMarkup(botones)

    await update.message.reply_text(
        "📄 *Carpetas OTS semanales*\n\n"
        "Selecciona la semana en la que deseas trabajar:",
        reply_markup=teclado,
        parse_mode="Markdown",
    )


# ============================================================
# RECIBIR PDF
# ============================================================

async def recibir_pdf(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    if update.message is None:
        return

    documento = update.message.document

    if documento is None:
        return

    nombre_archivo = documento.file_name or "documento.pdf"
    file_id = documento.file_id

    url_editor = f"{WEBAPP_URL}?file_id={file_id}"

    boton_editor = InlineKeyboardButton(
        text="✏️ Abrir editor de PDF",
        web_app=WebAppInfo(url=url_editor),
    )

    teclado = InlineKeyboardMarkup([[boton_editor]])

    await update.message.reply_text(
        f"PDF recibido correctamente:\n"
        f"{nombre_archivo}\n\n"
        "Presiona el botón para abrir la Mini App.",
        reply_markup=teclado,
    )


# ============================================================
# DOCUMENTOS NO VÁLIDOS
# ============================================================

async def documento_no_valido(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    if update.message is None:
        return

    await update.message.reply_text(
        "Envía únicamente archivos PDF."
    )


# ============================================================
# ERRORES
# ============================================================

async def manejar_error(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    logging.error(
        "Ocurrió un error en el bot:",
        exc_info=context.error,
    )


# ============================================================
# INICIO
# ============================================================

def main() -> None:

    if not TOKEN:
        raise ValueError(
            "No se encontró la variable TELEGRAM_BOT_TOKEN."
        )

    if not RENDER_URL:
        raise ValueError(
            "No se encontró la variable RENDER_EXTERNAL_URL."
        )

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("semanas", mostrar_semanas))

    app.add_handler(
        MessageHandler(
            filters.Document.MimeType("application/pdf"),
            recibir_pdf,
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Document.ALL,
            documento_no_valido,
        )
    )

    app.add_error_handler(manejar_error)

    webhook_path = "telegram"
    webhook_url = f"{RENDER_URL}/{webhook_path}"

    print("Bot activo mediante webhook.")
    print(f"Webhook: {webhook_url}")

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=webhook_path,
        webhook_url=webhook_url,
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
