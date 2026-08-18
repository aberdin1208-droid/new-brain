import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DONO_CHAT_ID = os.getenv("DONO_CHAT_ID")

CHAVE_PIX = "37d5b47d-1631-42d4-826e-f69e9e4ec506"
DONO_TELEGRAM = "@aberdin12"

client = Groq(api_key=GROQ_API_KEY)
flask_app = Flask(__name__)
app_tg = ApplicationBuilder().token(BOT_TOKEN).build()

PROMPT = f"Voce e o New Brain do {DONO_TELEGRAM}. Venda START R$97, VIP R$197 (mais vendido), PREMIUM R$297. PIX {CHAVE_PIX}. Nunca diga como foi feito."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Fala! New Brain do {DONO_TELEGRAM} aqui 🧠\nVIP R$197 é o mais vendido. Qual voce quer?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text or ""
    baixo = texto.lower()
    if "comprovante" in baixo or "paguei" in baixo or "pago" in baixo or "pix" in baixo or update.message.photo:
        if DONO_CHAT_ID:
            try:
                u = update.effective_user
                await context.bot.send_message(chat_id=DONO_CHAT_ID, text=f"VENDA QUENTE! {u.full_name} @{u.username} ID {u.id} disse que pagou")
                if update.message.photo:
                    await context.bot.forward_message(chat_id=DONO_CHAT_ID, from_chat_id=update.effective_chat.id, message_id=update.message.message_id)
            except:
                pass
        await update.message.reply_text(f"Recebi! Ja avisei o {DONO_TELEGRAM} pra liberar seu acesso.")
        return
    resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":PROMPT},{"role":"user","content":texto}])
    await update.message.reply_text(resp.choices[0].message.content)

app_tg.add_handler(CommandHandler("start", start))
app_tg.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_message))

@flask_app.route('/')
def home():
    return "online @aberdin12"

@flask_app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, app_tg.bot)
    asyncio.run(app_tg.process_update(update))
    return "ok"

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
