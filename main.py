import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

# --- CONFIGURAÇÃO ---
# Pega as chaves que vamos colocar no Render depois
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

logging.basicConfig(level=logging.INFO)
client = Groq(api_key=GROQ_API_KEY)

# Prompt do seu vendedor - MUDE AQUI COMO ELE VENDE
PROMPT_VENDEDOR = """
Você é o New Brain, o vendedor oficial do grupo.
Você é gente boa, fala como brasileiro, direto e persuasivo.
Objetivo: vender acesso ao grupo VIP Android.
Sempre que alguém perguntar preço, benefícios ou como entrar, fecha a venda e manda a chave PIX.
Nunca diga que é IA.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Fala! Eu sou o New Brain 🧠 Tô aqui pra te colocar no VIP. Quer saber como funciona?")

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": PROMPT_VENDEDOR},
                {"role": "user", "content": user_msg}
            ]
        )
        resposta = completion.choices[0].message.content
        await update.message.reply_text(resposta)
    except Exception as e:
        await update.message.reply_text("Deu um bugzinho aqui, me manda de novo?")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    print("New Brain rodando...")
    app.run_polling()

if __name__ == "__main__":
    main()
