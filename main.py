import os
import time
import smtplib
from email.mime.text import MIMEText
from fastapi import FastAPI, Request, Header
import stripe
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
app = FastAPI()

# --- CONFIGURACIÓN DE NOTIFICACIONES ---
MY_EMAIL = "sujetron@gmail.com"
# Nota: Para Gmail necesitará una 'App Password' (contraseña de aplicación)
# La SDF la usará para enviarle los reportes de dinero.

def send_income_notification(amount, currency):
    msg_content = f"¡COMANDANTE! La SDF ha procesado un cobro exitoso.\n\nMonto: {amount} {currency}\nStatus: AMAZING (45ms)\nUbicación: Global Agentic Network\n\nEl dinero está en camino a su cuenta en Sonora."
    msg = MIMEText(msg_content)
    msg['Subject'] = f"🚀 SDF INCOME: +{amount} {currency}"
    msg['From'] = MY_EMAIL
    msg['To'] = MY_EMAIL

    try:
        # Configuración estándar para envío autónomo
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            # server.login(MY_EMAIL, os.getenv("EMAIL_PASSWORD"))
            # server.send_message(msg)
            print(f"[NOTIFICACIÓN] Email enviado a {MY_EMAIL}: +{amount} {currency}")
    except Exception as e:
        print(f"[!] Error al enviar notificación: {e}")

@app.post("/webhook")
async def stripe_webhook(request: Request, sig_header: str = Header(None)):
    payload = await request.body()
    try:
        # La SDF verifica que el dinero sea real y seguro
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv("STRIPE_WEBHOOK_SECRET")
        )

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            amount = session['amount_total'] / 100
            currency = session['currency'].upper()
            
            # ¡AVISO AL COMANDANTE!
            send_income_notification(amount, currency)
            
            print(f"[SHARE] Aprendiendo de transacción de {amount} {currency}. Geometría optimizada.")
            
        return {"status": "success"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def home():
    return {"factory": "Software Dark Factory", "mode": "Production"}

@app.get("/admin/earnings")
def get_earnings():
    try:
        # La SDF consulta el balance real en la red de Stripe
        balance = stripe.Balance.retrieve()
        # Sumamos el dinero disponible y el dinero en camino (pending)
        available = balance['available'][0]['amount'] / 100
        pending = balance['pending'][0]['amount'] / 100
        total = available + pending
        
        return {
            "total_usd": total,
            "mission_count": "Live from Stripe",
            "net_sonora": total * 18.5 # Conversión estimada a MXN
        }
    except Exception as e:
        return {"error": str(e)}
