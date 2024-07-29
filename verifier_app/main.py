from bitcoinutils.setup import setup
from fastapi import FastAPI

from bitvmx_protocol_library.config import common_protocol_properties
from bitvmx_protocol_library.enums import BitcoinNetwork
from verifier_app.api.router import router as verifier_router

if common_protocol_properties.network == BitcoinNetwork.MUTINYNET:
    setup("testnet")
else:
    setup(common_protocol_properties.network.value)

app = FastAPI(
    title="Verifier service",
    description="Microservice to perform all the operations related to the verifier",
)


@app.get("/healthcheck")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(verifier_router, prefix="/api")  # , tags=["Prover API"])
