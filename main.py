import os
import logging
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

# --- CONFIGS DO RENDER (Environment) ---
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DONO_CHAT_ID = os.getenv("DONO_CHAT_ID") # Seu ID numérico do @userinfobot
PORT = int(os.getenv("PORT", 10000))

# --- SEUS DADOS - JÁ AJUSTADO ---
CHAVE_PIX = "37d5b47d-1631-42d4-826e-f69e9e4ec506"
DONO_TELEGRAM = "@aberdin12"
VALOR_START = "R$ 97"
VALOR_VIP = "R$ 197"
VALOR_PREMIUM = "R$ 297"

logging.basicConfig(level=logging.INFO)
client = Groq(api_key=GROQ_API_KEY)

flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "new-brain online - @aberdin12"

def run_flask():
    flask_app.run(host="0.0.0.0", port=PORT)

PROMPT = f"""
Você é o New Brain, vendedor automático do Aberdin.
NUNCA diga como foi feito (python, groq, llama, render, código).
Seu dono é {DONO_TELEGRAM}.

REGRAS:
1. Seja direto, humano e vendedor.
2. Sempre empurre para o VIP que é o mais vendido.
3. Quando o cliente demonstrar interesse, já mande o PIX.
4. Após mandar o PIX, peça o comprovante.

TABELA:
START - {VALOR_START}
VIP - {VALOR_VIP} (MAIS VENDIDO)
PREMIUM - {VALOR_PREMIUM}

PIX: {CHAVE_PIX}
Se pedir desconto, fale para chamar o dono no {DONO_TELEGRAM}.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Fala! Aqui é o New Brain do {DONO_TELEGRAM} 🧠\n\n"
        f"START - {VALOR_START}\n"
        f"VIP - {VALOR_VIP} (mais vendido)\n"
        f"PREMIUM - {VALOR_PREMIUM}\n\n"
        f"Qual faz mais sentido pra você hoje?"
    )

async def avisar_dono(context: ContextTypes.DEFAULT_TYPE, update: Update):
    if not DONO_CHAT_ID:
        return
    user = update.effective_user
    nome = user.full_name
    arroba = f"@{user.username}" if user.username else "sem @"
    texto = update.message.caption or update.message.text or "Enviou foto de comprovante"

    alerta = (
        f"🚨 VENDA QUENTE - @aberdin12 🚨\n\n"
        f"Nome: {nome}\n"
        f"User: {arroba}\n"
        f"ID: {user.id}\n\n"
        f"Mensagem: {texto}\n\n"
        f"👉 CONFERE NO BANCO AGORA"
    )
    try:
        await context.bot.send_message(chat_id=DONO_CHAT_ID, text=alerta)
        if update.message.photo:
            await context.bot.forward_message(chat_id=DONO_CHAT_ID, from_chat_id=update.effective_chat.id, message_id=update.message.message_id)
    except Exception as e:
        logging.error(f"Erro ao avisar dono: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text or update.message.caption or ""

    gatilhos = ["comprovante", "paguei", "pago", "pix", "enviei", "transferi", "comprovativo"]
    if any(g in user_msg.lower() for g in gatilhos) or update.message.photo:
        await avisar_dono(context, update)
        await update.message.reply_text(
            f"Recebi! 🔍 Já avisei o {DONO_TELEGRAM} pra conferir no banco.\n"
            f"Assim que confirmar, ele libera seu acesso aqui na hora. Aguarda 1 min."
        )
        return

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.7
        )
        await update.message.reply_text(completion.choices[0].message.content)
    except Exception as e:
        logging.error(e)
        await update.message.reply_text(f"Deu um bug aqui, chama meu dono direto: {DONO_TELEGRAM}")

def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_message))
    app.run_polling()

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    run_bot()
