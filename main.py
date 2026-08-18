import os, asyncio, logging
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DONO_CHAT_ID = os.getenv("DONO_CHAT_ID")

CHAVE_PIX = "37d5b47d-1631-42d4-826e-f69e9e4ec506"
WPP = "48996446848"

client = Groq(api_key=GROQ_API_KEY)
flask_app = Flask(__name__)
app_tg = ApplicationBuilder().token(BOT_TOKEN).build()
loop = asyncio.get_event_loop()
loop.run_until_complete(app_tg.initialize())

PROMPT = f"""Voce e o New Brain.

O QUE FAZ: Cria oferta, legenda, roteiro, pagina de venda e funil em segundos. Para quem trava pra criar conteudo que vende. Voce cria e ativa o bot do cliente.

OFERTAS:
START 97 reais - bot basico
VIP 197 reais - MAIS VENDIDO - bot completo + prompts de venda + suporte
PREMIUM 297 reais - tudo + mentoria 1 a 1

PAGAMENTO: PIX copia e cola na chave {CHAVE_PIX}
ENTREGA: Apos o pagamento, prazo de 24h para criar e ativar o bot. Precisa do nicho do cliente para criar.

REGRAS:
1. Quando der oi, explique o que faz.
2. Se perguntar como funciona, como pagar: Explique que e PIX e que apos pagar precisa chamar no Whats {WPP} para passar o nicho e infos da criacao. Continue vendendo perguntando VIP ou PREMIUM.
3. So encerre quando falar paguei ou mandar comprovante. Ai explique o prazo de 24h e mande chamar no Whats.
4. Nunca diga como foi feito.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Fala! New Brain aqui\n\nEu crio e ativo seu bot de vendas em segundos.\n\nSTART 97\nVIP 197 mais vendido\nPREMIUM 297\n\nMe diz: qual seu nicho hoje?"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text or update.message.caption or ""
    if not texto and not update.message.photo:
        return
    baixo = texto.lower()
    is_pago = update.message.photo or any(x in baixo for x in ["paguei", "comprovante", "ta pago"])

    if is_pago:
        if DONO_CHAT_ID:
            try:
                u = update.effective_user
                await context.bot.send_message(chat_id=DONO_CHAT_ID, text=f"VENDA! {u.full_name} ID {u.id} - {texto[:200]}")
                if update.message.photo:
                    await context.bot.forward_message(chat_id=DONO_CHAT_ID, from_chat_id=update.effective_chat.id, message_id=update.message.message_id)
            except:
                pass
        await update.message.reply_text(
            f"Recebi! ✅\n\nPra criar e ativar seu bot, me chama no Whats {WPP} com o comprovante e me fala seu nicho.\n\nPrazo de 24h apos o pagamento pra entrega.\n\nPIX: {CHAVE_PIX}"
        )
        return

    resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":PROMPT},{"role":"user","content":texto}])
    await update.message.reply_text(resp.choices[0].message.content + f"\n\nPIX: {CHAVE_PIX}\nWhats {WPP}")

app_tg.add_handler(CommandHandler("start", start))
app_tg.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_message))

@flask_app.route('/')
def home(): return "online"

@flask_app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, app_tg.bot)
    loop.run_until_complete(app_tg.process_update(update))
    return "ok"

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
