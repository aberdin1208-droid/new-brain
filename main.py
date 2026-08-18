import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq
import asyncio

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DONO_CHAT_ID = os.getenv("DONO_CHAT_ID")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL") # O Render cria isso sozinho

CHAVE_PIX = "37d5b47d-1631-42d4-826e-f69e9e4ec506"
DONO_TELEGRAM = "@aberdin12"

client = Groq(api_key=GROQ_API_KEY)
flask_app = Flask(__name__)
app_tg = ApplicationBuilder().token(BOT_TOKEN).build()

PROMPT = f"Você é o New Brain do {DONO_TELEGRAM}. Venda START R$97, VIP R$197, PREMIUM R$297. PIX {CHAVE_PIX}. Seja vendedor direto."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Fala! Sou o New Brain do {DONO_TELEGRAM} 🧠 VIP R$197 mais vendido.")

async def avisar_dono(context, update):
    if not DONO_CHAT_ID: return
    u = update.effective_user
    await context.bot.send_message(chat_id=DONO_CHAT_ID, text=f"🚨 VENDA! {u.full_name} @{u.username} pagou. Confere!")
    if update.message.photo:
        await context.bot.forward_message(chat_id=DONO_CHAT_ID, from_chat_id=update.effective_chat.id, message_id=update.message.message_id)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text or ""
    if any(x in txt.lower() for x in ["comprovante","paguei","pago"]) or update.message.photo:
        await avisar_dono(context, update)
        await update.message.reply_text(f"Recebi! Avisei o {DONO_TELEGRAM}")
        return
    r = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":PROMPT},{"role":"user","content":txt}])
    await update.message.reply_text(r.choices[0].message.content)

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

@flask_app.route('/setwebhook')
def set_webhook():
    url = f"{RENDER_URL}/webhook"
    asyncio.run(app_tg.bot.set_webhook(url=url, drop_pending_updates=True))
    return f"webhook setado em {url}"

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
