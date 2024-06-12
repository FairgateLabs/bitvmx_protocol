from fastapi import FastAPI

app = FastAPI(
    title="Verifier service",
    description="Microservice to perform all the operations related to the verifier",
)


@app.get("/healthcheck")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
