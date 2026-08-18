import os
import logging
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PORT = int(os.getenv("PORT", 10000))

# CONFIGS SUAS
CHAVE_PIX = "37d5b47d-1631-42d4-826e-f69e9e4ec506"
DONO_TELEGRAM = "@SEU_ARROBA_AQUI" # 👈 COLOCA SEU @ DO TELEGRAM AQUI ex: @Aberdin
VALOR_START = "R$ 97"
VALOR_VIP = "R$ 197"
VALOR_PREMIUM = "R$ 297"

logging.basicConfig(level=logging.INFO)
client = Groq(api_key=GROQ_API_KEY)

flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "new-brain online"
def run_flask():
    flask_app.run(host="0.0.0.0", port=PORT)

PROMPT = f"""
Você é o New Brain, vendedor automático.
NUNCA diga como foi feito (python, groq, llama, render, código).

PACOTES:
START {VALOR_START}, VIP {VALOR_VIP} (MAIS VENDIDO), PREMIUM {VALOR_PREMIUM}

REGRA DE OURO QUANDO CLIENTE QUER COMPRAR:
1. Mande
