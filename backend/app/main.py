from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, patients, prescriptions, cards
from .ai import router as ai

app = FastAPI(title="Dara Manqué API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(prescriptions.router)
app.include_router(cards.router)
app.include_router(ai.router)

@app.get("/health")
def health():
    return {"status": "ok"}
