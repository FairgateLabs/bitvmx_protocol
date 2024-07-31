from bitcoinutils.setup import setup
from fastapi import FastAPI

from bitvmx_protocol_library.config import common_protocol_properties
from bitvmx_protocol_library.enums import BitcoinNetwork
from prover_app.api.router import router as prover_router

if common_protocol_properties.network == BitcoinNetwork.MUTINYNET:
    setup("testnet")
else:
    setup(common_protocol_properties.network.value)

app = FastAPI(
    title="Prover service",
    description="Microservice to perform all the operations related to the prover",
)


@app.get("/healthcheck")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(prover_router, prefix="/api")  # , tags=["Prover API"])
