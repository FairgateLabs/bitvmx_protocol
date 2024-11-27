from bitcoinutils.keys import PublicKey

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from bitvmx_protocol_library.transaction_generation.entities.dtos.bitvmx_prover_signatures_dto import (
    BitVMXProverSignaturesDTO,
)
from bitvmx_protocol_library.transaction_generation.services.signature_verification.verify_signature_service import (
    VerifySignatureService,
)


class VerifyProverSignaturesService:

    def __init__(self, destroyed_public_key: PublicKey):
        self.unspendable_public_key = destroyed_public_key
        self.verify_signature_service = VerifySignatureService(
            unspendable_public_key=destroyed_public_key
        )

    def __call__(
        self,
        public_key: str,
        bitvmx_prover_signatures_dto: BitVMXProverSignaturesDTO,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
    ):

        funding_result_output_amount = (
            bitvmx_protocol_setup_properties_dto.funding_amount_of_satoshis
        )
        trigger_protocol_script = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_protocol_scripts_list[
            bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_protocol_index()
        ]
        trigger_protocol_script_address = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_protocol_scripts_list.get_taproot_address(
            public_key=self.unspendable_public_key
        )

        self.verify_signature_service(
            tx=bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_protocol_tx,
            script=trigger_protocol_script,
            script_address=trigger_protocol_script_address,
            amount=funding_result_output_amount
            - bitvmx_protocol_setup_properties_dto.step_fees_satoshis,
            public_key_hex=public_key,
            signature=bitvmx_prover_signatures_dto.trigger_protocol_signature,
        )

        for i in range(len(bitvmx_prover_signatures_dto.search_choice_signatures)):
            script = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.choice_search_scripts_list(
                iteration=i
            )[
                bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.choice_search_script_index()
            ]
            script_address = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.choice_search_scripts_list(
                iteration=i
            ).get_taproot_address(
                public_key=self.unspendable_public_key
            )
            self.verify_signature_service(
                tx=bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.search_choice_tx_list[
                    i
                ],
                script=script,
                script_address=script_address,
                amount=funding_result_output_amount
                - (3 + 2 * i) * bitvmx_protocol_setup_properties_dto.step_fees_satoshis,
                public_key_hex=public_key,
                signature=bitvmx_prover_signatures_dto.search_choice_signatures[i],
            )

        script = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_challenge_scripts[
            0
        ]
        script_address = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_trace_challenge_address(
            destroyed_public_key=self.unspendable_public_key
        )

        self.verify_signature_service(
            tx=bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_execution_challenge_tx,
            script=script,
            script_address=script_address,
            amount=funding_result_output_amount
            - (2 * len(bitvmx_prover_signatures_dto.search_choice_signatures) + 3)
            * bitvmx_protocol_setup_properties_dto.step_fees_satoshis,
            public_key_hex=public_key,
            signature=bitvmx_prover_signatures_dto.trigger_execution_challenge_signature,
        )

        script = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_trace_challenge_scripts_list[
            bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_read_search_challenge_index()
        ]
        script_address = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_trace_challenge_address(
            destroyed_public_key=self.unspendable_public_key
        )

        self.verify_signature_service(
            tx=bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.read_search_choice_tx_list[
                0
            ],
            script=script,
            script_address=script_address,
            amount=funding_result_output_amount
            - (2 * len(bitvmx_prover_signatures_dto.search_choice_signatures) + 3)
            * bitvmx_protocol_setup_properties_dto.step_fees_satoshis,
            public_key_hex=public_key,
            signature=bitvmx_prover_signatures_dto.read_search_choice_signatures[0],
        )

        for i in range(len(bitvmx_prover_signatures_dto.search_choice_signatures) - 1):
            current_read_search_choice_script_list = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.choice_read_search_script_list(
                iteration=i + 1
            )
            current_read_search_choice_script_address = (
                current_read_search_choice_script_list.get_taproot_address(
                    public_key=self.unspendable_public_key
                )
            )
            current_read_search_choice_index = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.choice_read_search_script_index(
                iteration=i + 1
            )
            current_read_search_choice_script = current_read_search_choice_script_list[
                current_read_search_choice_index
            ]
            self.verify_signature_service(
                tx=bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.read_search_choice_tx_list[
                    i + 1
                ],
                script=current_read_search_choice_script,
                script_address=current_read_search_choice_script_address,
                amount=funding_result_output_amount
                - (2 + 2 * len(bitvmx_prover_signatures_dto.search_choice_signatures) + 3 + 2 * i)
                * bitvmx_protocol_setup_properties_dto.step_fees_satoshis,
                public_key_hex=public_key,
                signature=bitvmx_prover_signatures_dto.read_search_choice_signatures[i + 1],
            )
