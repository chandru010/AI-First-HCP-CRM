from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import agent, hcp, interactions
from app.core.config import settings
from app.core.database import Base, engine
from app.services.seed import seed_demo_data


Base.metadata.create_all(bind=engine)
seed_demo_data()

app = FastAPI(title=settings.app_name, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(hcp.router, prefix="/api/hcps", tags=["HCPs"])
app.include_router(interactions.router, prefix="/api/interactions", tags=["Interactions"])
app.include_router(agent.router, prefix="/api/agent", tags=["LangGraph Agent"])


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "model": settings.groq_model}
