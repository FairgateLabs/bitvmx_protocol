from typing import List

from pydantic import BaseModel


class BitVMXProtocolSetupPropertiesDTO(BaseModel):
    setup_uuid: str
    funding_amount_of_satoshis: int
    step_fees_satoshis: int
    funding_tx_id: str
    funding_index: int
    verifier_list: List[str]
    # controlled_prover_address: str
    # controlled_verifier_address: str
    # destroyed_prover_public_key: str
    # destroyed_verifier_public_key: str
