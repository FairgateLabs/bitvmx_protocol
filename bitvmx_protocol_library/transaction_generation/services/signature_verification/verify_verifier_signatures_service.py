from bitcoinutils.keys import PublicKey

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from bitvmx_protocol_library.script_generation.entities.dtos.bitvmx_bitcoin_scripts_dto import (
    BitVMXBitcoinScriptsDTO,
)
from bitvmx_protocol_library.transaction_generation.services.signature_verification.verify_signature_service import (
    VerifySignatureService,
)


class VerifyVerifierSignaturesService:

    def __init__(self, unspendable_public_key: PublicKey):
        self.unspendable_public_key = unspendable_public_key
        self.verify_signature_service = VerifySignatureService(
            unspendable_public_key=unspendable_public_key
        )

    def __call__(
        self,
        public_key: str,
        hash_result_signature: str,
        search_hash_signatures: str,
        trace_signature: str,
        bitvmx_bitcoin_scripts_dto: BitVMXBitcoinScriptsDTO,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
    ):

        funding_result_output_amount = (
            bitvmx_protocol_setup_properties_dto.funding_amount_of_satoshis
        )
        script = bitvmx_bitcoin_scripts_dto.hash_result_script
        script_address = self.unspendable_public_key.get_taproot_address([[script]])

        self.verify_signature_service(
            tx=bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.hash_result_tx,
            script=bitvmx_bitcoin_scripts_dto.hash_result_script,
            script_address=script_address,
            amount=funding_result_output_amount,
            public_key_hex=public_key,
            signature=hash_result_signature,
        )

        for i in range(len(search_hash_signatures)):
            script = bitvmx_bitcoin_scripts_dto.hash_search_scripts[i]
            script_address = self.unspendable_public_key.get_taproot_address([[script]])
            self.verify_signature_service(
                tx=bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.search_hash_tx_list[
                    i
                ],
                script=script,
                script_address=script_address,
                amount=funding_result_output_amount
                - (2 + 2 * i) * bitvmx_protocol_setup_properties_dto.step_fees_satoshis,
                public_key_hex=public_key,
                signature=search_hash_signatures[i],
            )

        script = bitvmx_bitcoin_scripts_dto.trace_script
        script_address = self.unspendable_public_key.get_taproot_address([[script]])

        self.verify_signature_service(
            tx=bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trace_tx,
            script=script,
            script_address=script_address,
            amount=funding_result_output_amount
            - (2 + 2 * len(search_hash_signatures))
            * bitvmx_protocol_setup_properties_dto.step_fees_satoshis,
            public_key_hex=public_key,
            signature=trace_signature,
        )
