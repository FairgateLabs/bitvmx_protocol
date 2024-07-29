from fastapi import FastAPI

from prover_app.api.router import router as prover_router

app = FastAPI(
    title="Prover service",
    description="Microservice to perform all the operations related to the prover",
)


@app.get("/healthcheck")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(prover_router, prefix="/api")  # , tags=["Prover API"])
