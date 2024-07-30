from pydantic import BaseModel


class BitVmxProtocolSetupPropertiesDTO(BaseModel):
    setup_uuid: str
    funding_amount_satoshis: int
    step_fees_satoshis: int
    funding_tx_id: str
    funding_index: int
    controlled_prover_address: str
    controlled_verifier_address: str
