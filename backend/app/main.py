from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, patients, prescriptions, cards
from .ai import router as ai
from .ai import engine as ai_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Fail-fast: charge les modèles/CSV IA au démarrage plutôt qu'à la
    # première requête, pour qu'un artefact manquant ou corrompu fasse
    # échouer le boot bruyamment (cf. spec §Gestion des erreurs).
    ai_engine._load()
    yield


app = FastAPI(title="Dara Manqué API", version="1.0.0", lifespan=lifespan)

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
