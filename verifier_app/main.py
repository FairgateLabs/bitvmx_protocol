from fastapi import FastAPI

from verifier_app.api.router import router as verifier_router

app = FastAPI(
    title="Verifier service",
    description="Microservice to perform all the operations related to the verifier",
)


@app.get("/healthcheck")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(verifier_router, prefix="/api")  # , tags=["Prover API"])
