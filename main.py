import os
import logging
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DONO_CHAT_ID = os.getenv("DONO_CHAT_ID")
PORT = int(os.getenv("PORT", 10000))

CHAVE_PIX = "37d5b47d-1631-42d4-826e-f69e9e4ec506"
DONO_TELEGRAM = "@aberdin12"

logging.basicConfig(level=logging.INFO)
client = Groq(api_key=GROQ_API_KEY)

flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "new-brain @aberdin12 online"

def run_flask():
    flask_app.run(host="0.0.0.0", port=PORT)

PROMPT = f"""
Você é o New Brain, vendedor do {DONO_TELEGRAM}.
Planos: START R$97, VIP R$197 (mais vendido), PREMIUM R$297.
PIX: {CHAVE_PIX}
Nunca explique como foi feito. Seja vendedor.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Fala! Sou o New Brain do {DONO_TELEGRAM} 🧠\nVIP R$197 é o mais vendido. Qual você quer hoje?")

async def avisar_dono(context, update):
    if not DONO_CHAT_ID:
        return
    u = update.effective_user
    try:
        await context.bot.send_message(chat_id=DONO_CHAT_ID, text=f"🚨 VENDA QUENTE!\nNome: {u.full_name}\nUser: @{u.username}\nID: {u.id}\nMsg: {update.message.text or 'Enviou foto'}")
        if update.message.photo:
            await context.bot.forward_message(chat_id=DONO_CHAT_ID, from_chat_id=update.effective_chat.id, message_id=update.message.message_id)
    except Exception as e:
        logging.error(f"Erro aviso dono: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text or ""
    txt_low = texto.lower()
    if any(p in txt_low for p in ["comprovante", "paguei", "pago", "pix feito", "enviei"]) or update.message.photo:
        await avisar_dono(context, update)
        await update.message.reply_text(f"Recebi! Já avisei o {DONO_TELEGRAM} pra conferir no banco e liberar seu acesso.")
        return

    try:
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": texto}
            ]
        )
        await update.message.reply_text(resp.choices[0].message.content)
    except Exception as e:
        logging.error(e)
        await update.message.reply_text(f"Deu bug, chama o dono: {DONO_TELEGRAM}")

async def post_init(application):
    await application.bot.delete_webhook(drop_pending_updates=True)

def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_message))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    run_bot()
