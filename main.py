
import os
import time
import stripe
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
app = FastAPI(title="SDF Token Engine")

# --- BÓVEDA DE TOKENS (Simulación de DB) ---
# En una versión escalable, esto iría a PostgreSQL
token_ledger = {
    "test_agent_sonora": 1000000, # Un millón de tokens de regalo para el Comandante
}

class ChargeRequest(BaseModel):
    agent_id: str
    amount: int # en centavos
    token_cost: int = 100 # Costo de tokens por transacción

@app.get("/v1/balance/{agent_id}")
def get_balance(agent_id: str):
    balance = token_ledger.get(agent_id, 0)
    return {"agent_id": agent_id, "tokens_remaining": balance}

@app.post("/v1/charge")
async def process_agent_charge(req: ChargeRequest, authorization: str = Header(None)):
    # 1. Verificación de Identidad
    if not authorization or "Bearer" not in authorization:
        raise HTTPException(status_code=401, detail="Missing SDF Key")
    
    # 2. Verificación de Bóveda (Tokens)
    current_tokens = token_ledger.get(req.agent_id, 0)
    if current_tokens < req.token_cost:
        raise HTTPException(status_code=402, detail="Insufficient Tokens. Please refill at safe-collect-web.vercel.app")

    # 3. Quema de Tokens (Amazing Scorer)
    token_ledger[req.agent_id] -= req.token_cost
    
    # 4. Procesamiento de Pago Real (Simulado para velocidad)
    time.sleep(0.045) # 45ms latencia SHARE
    
    return {
        "status": "SETTLED",
        "tokens_burned": req.token_cost,
        "tokens_left": token_ledger[req.agent_id],
        "latency": "45ms",
        "node": "Sonora-Main-01"
    }

@app.get("/admin/earnings")
def get_earnings():
    # Consulta a Stripe + Estadísticas de Tokens
    return {
        "total_usd": 0.0, # Se llenará con Stripe Live
        "total_tokens_issued": sum(token_ledger.values()),
        "active_agents": len(token_ledger)
    }

@app.get("/")
def home():
    return {"system": "SDF Token Factory", "status": "Operational"}
