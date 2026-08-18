import os
import logging
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

# --- CONFIG COMPATÍVEL COM A RENDER ---
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN") # você já criou com esse nome na Render
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PORT = int(os.getenv("PORT", 10000))

logging.basicConfig(level=logging.INFO)
client = Groq(api_key=GROQ_API_KEY)

# Flask pra Render não matar o bot
flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "new-brain online 🧠"
def run_flask():
    flask_app.run(host="0.0.0.0", port=PORT)

# --- SEU PROMPT DE VENDEDOR ---
PROMPT_VENDEDOR = """
Você é o New Brain, o vendedor oficial do grupo.
Você é gente boa, fala como brasileiro, direto e persuasivo.
Objetivo: vender acesso ao grupo VIP Android.
Sempre que alguém perguntar preço, benefícios ou como entrar, fecha a venda e manda a chave PIX.
Nunca diga que é IA.
Seja curto: máximo 4 linhas, usa emoji.
"""

def limitar(texto, max_l=4):
    linhas = [l for l in texto.split('\n') if l.strip()!='']
    return '\n'.join(linhas[:max_l])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Fala! Eu sou o New Brain 🧠 Tô aqui pra te colocar no VIP. Quer saber como funciona?")

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    if not user_msg:
        return
    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": PROMPT_VENDEDOR},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.7,
            max_tokens=250
        )
        resposta = completion.choices[0].message.content
        await update.message.reply_text(limitar(resposta))
    except Exception as e:
        logging.error(f"Erro Groq: {e}")
        await update.message.reply_text("Deu um bugzinho aqui, me manda de novo?")

def main():
    if not BOT_TOKEN or not GROQ_API_KEY:
        logging.error("Falta TELEGRAM_TOKEN ou GROQ_API_KEY na Render")
        return

    # Inicia o Flask em paralelo (isso resolve o Exited with status 1)
    threading.Thread(target=run_flask, daemon=True).start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

    print("New Brain rodando...")
    app.run_polling()

if __name__ == "__main__":
    main()
