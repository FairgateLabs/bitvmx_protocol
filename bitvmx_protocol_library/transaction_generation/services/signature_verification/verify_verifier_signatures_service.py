from typing import List

from bitcoinutils.keys import PublicKey

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
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
        search_hash_signatures: List[str],
        trace_signature: str,
        read_search_hash_signatures: List[str],
        read_trace_signature: str,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
    ):

        funding_result_output_amount = (
            bitvmx_protocol_setup_properties_dto.funding_amount_of_satoshis
        )
        script = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.hash_result_script
        script_address = self.unspendable_public_key.get_taproot_address([[script]])

        self.verify_signature_service(
            tx=bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.hash_result_tx,
            script=bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.hash_result_script,
            script_address=script_address,
            amount=funding_result_output_amount,
            public_key_hex=public_key,
            signature=hash_result_signature,
        )

        for i in range(len(search_hash_signatures)):
            script = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.hash_search_scripts_list(
                iteration=i
            )[
                bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.hash_search_script_index()
            ]
            script_address = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.hash_search_scripts_list(
                iteration=i
            ).get_taproot_address(
                public_key=self.unspendable_public_key
            )
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

        script = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trace_script_list[
            bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trace_script_index()
        ]
        script_address = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trace_script_list.get_taproot_address(
            public_key=self.unspendable_public_key
        )

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

        for i in range(len(search_hash_signatures) - 1):
            script = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.hash_read_search_scripts_list(
                iteration=i
            )[
                bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.hash_read_search_script_index()
            ]
            script_address = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.hash_read_search_scripts_list(
                iteration=i
            ).get_taproot_address(
                public_key=self.unspendable_public_key
            )
            self.verify_signature_service(
                tx=bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.read_search_hash_tx_list[
                    i
                ],
                script=script,
                script_address=script_address,
                amount=funding_result_output_amount
                - (
                    2
                    + 2
                    * len(
                        bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.search_hash_tx_list
                    )
                    + 2
                    + 2 * i
                )
                * bitvmx_protocol_setup_properties_dto.step_fees_satoshis,
                public_key_hex=public_key,
                signature=read_search_hash_signatures[i],
            )

        read_trace_script_address = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.read_trace_script_list.get_taproot_address(
            self.unspendable_public_key
        )
        read_trace_script_index = (
            bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.read_trace_script_index()
        )
        self.verify_signature_service(
            tx=bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.read_trace_tx,
            script=bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.read_trace_script_list[
                read_trace_script_index
            ],
            script_address=read_trace_script_address,
            amount=(
                funding_result_output_amount
                - (
                    2
                    + 2
                    * len(
                        bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.search_hash_tx_list
                    )
                    + 2
                    + 2
                    * len(
                        bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.read_search_hash_tx_list
                    )
                )
                * bitvmx_protocol_setup_properties_dto.step_fees_satoshis
            ),
            public_key_hex=public_key,
            signature=read_trace_signature,
        )
