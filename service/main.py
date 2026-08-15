from fastapi import FastAPI

from routes.filament import router

app = FastAPI(title="Atropos Service")
app.include_router(router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
