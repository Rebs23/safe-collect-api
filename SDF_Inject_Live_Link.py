import os
import stripe
import re
from dotenv import load_dotenv

# 1. Cargar Credenciales Reales (.env)
load_dotenv()

# Configuramos la API Key de Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def inject_live_link():
    print("[*] SDF: Iniciando Inyección de Vuelo (Modo Producción)...")
    
    try:
        # A. Crear el Producto 'Amazing' en el catálogo real de Stripe
        print("[*] SDF: Registrando producto en la red global de Stripe...")
        product = stripe.Product.create(
            name="Safe-Collect Premium Engine [SDF v1.1]",
            description="Autonomous Space-Grade Payment Infrastructure",
        )

        # B. Crear el Precio (50 USD)
        price = stripe.Price.create(
            product=product.id,
            unit_amount=5000, # $50.00 USD
            currency="usd",
        )

        # C. Crear el Payment Link Permanente
        print("[*] SDF: Generando Payment Link de alta conversión...")
        payment_link = stripe.PaymentLink.create(
            line_items=[{"price": price.id, "quantity": 1}],
            after_completion={"type": "redirect", "redirect": {"url": "https://safe-collect-web.vercel.app"}},
        )

        live_url = payment_link.url
        print("\n[✔] SUCCESS: Link de Producción Creado:")
        print(live_url)

        # D. Inyectar el Link en el archivo index.html
        print("\n[*] SDF: Modificando index.html para el despliegue global...")
        with open("index.html", "r", encoding="utf-8") as f:
            html = f.read()

        # Reemplazamos los links locales por el link real de Stripe
        # Buscamos todas las ocurrencias de http://localhost:8000/docs
        new_html = html.replace('http://localhost:8000/docs', live_url)
        
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(new_html)

        separador = "=" * 60
        print("\n" + separador)
        print("SDF: Website actualizada con éxito. ¡Lista para facturar!")
        print(separador)
        print("\nPRÓXIMO PASO: Escriba 'vercel --prod' en su terminal.")
        print(separador)

    except Exception as e:
        print("\n[✘] ERROR CRÍTICO DE LA SDF: " + str(e))
        print("Pista: Verifique que su llave Live de Stripe en el .env sea correcta.")

if __name__ == "__main__":
    inject_live_link()
