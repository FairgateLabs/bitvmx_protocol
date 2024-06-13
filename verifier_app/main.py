from fastapi import FastAPI

app = FastAPI(
    title="Verifier service",
    description="Microservice to perform all the operations related to the verifier",
)


@app.get("/healthcheck")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/create_setup")
async def create_setup(setup_uuid: str) -> dict[str, str]:
    return {"id": setup_uuid}
