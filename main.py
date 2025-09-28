import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
import os
from threading import Thread

# Configuración del log
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Token desde variables de entorno (más seguro que ponerlo directo en el código)
TOKEN = os.environ.get("TOKEN")

# Flask para mantener el servicio vivo en Fly.io
app = Flask(name)

@app.route("/")
def home():
    return "✅ Bot de Telegram corriendo en Fly.io!"

# Funciones del bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hola, envíame un número de cédula para consultar.")

async def consultar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cedula = update.message.text.strip()
    url = f"https://comunicaciones.davivienda.com/white-list-aprobacion?cedula={cedula}"

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            await update.message.reply_text(f"🔎 Resultado: {response.text}")
        else:
            await update.message.reply_text("⚠️ Error al consultar la cédula.")
    except Exception as e:
        await update.message.reply_text(f"❌ Ocurrió un error: {e}")

def main():
    application = Application.builder().token(TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, consultar))

    # Iniciar el bot
    application.run_polling()

if name == "main":
    port = int(os.environ.get("PORT", 5000))
    Thread(target=lambda: app.run(host="0.0.0.0", port=port)).start()
    main()
