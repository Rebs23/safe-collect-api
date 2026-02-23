import os
import asyncio
import stripe
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
app = FastAPI(title="SDF Token Engine")

token_ledger = {"test_agent_sonora": 1000000}
ledger_lock = asyncio.Lock()
security = HTTPBearer()

class ChargeRequest(BaseModel):
    agent_id: str
    amount: int
    token_cost: int = 100

async def verify_sdf_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != os.getenv("SDF_MASTER_KEY"):
        raise HTTPException(status_code=401, detail="Invalid SDF Key")
    return credentials.credentials

@app.get("/v1/balance/{agent_id}")
async def get_balance(agent_id: str):
    async with ledger_lock:
        balance = token_ledger.get(agent_id, 0)
    return {"agent_id": agent_id, "tokens_remaining": balance}

@app.post("/v1/charge", dependencies=[Depends(verify_sdf_key)])
async def process_agent_charge(req: ChargeRequest):
    async with ledger_lock:
        current_tokens = token_ledger.get(req.agent_id, 0)
        if current_tokens < req.token_cost:
            raise HTTPException(
                status_code=402, 
                detail="Insufficient Tokens. Please refill at safe-collect-web.vercel.app"
            )

        token_ledger[req.agent_id] -= req.token_cost
        await asyncio.sleep(0.045)
        tokens_left = token_ledger[req.agent_id]
    
    return {
        "status": "SETTLED", 
        "tokens_burned": req.token_cost, 
        "tokens_left": tokens_left,
        "latency": "45ms",
        "node": "Sonora-Main-01"
    }

@app.get("/admin/earnings", dependencies=[Depends(verify_sdf_key)])
async def get_earnings():
    async with ledger_lock:
        total_tokens = sum(token_ledger.values())
        active_agents = len(token_ledger)
    return {
        "total_usd": 0.0,
        "total_tokens_issued": total_tokens,
        "active_agents": active_agents
    }

@app.post("/v1/fiat/checkout")
async def fiat_checkout():
    return {
        "id": "pi_mock_555",
        "client_secret": "pi_mock_555_secret_777",
        "status": "requires_payment_method",
        "amount": 5000,
        "currency": "usd"
    }

@app.get("/")
def home():
    return {"system": "SDF Token Factory", "status": "Operational"}
