from bitcoinutils.constants import TAPROOT_SIGHASH_ALL

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from bitvmx_protocol_library.transaction_generation.entities.dtos.bitvmx_signatures_dto import (
    BitVMXSignaturesDTO,
)


class GenerateSignaturesService:

    def __init__(self, private_key, destroyed_public_key):
        self.private_key = private_key
        self.destroyed_public_key = destroyed_public_key

    def __call__(
        self,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
    ):

        funding_result_output_amount = (
            bitvmx_protocol_setup_properties_dto.funding_amount_of_satoshis
        )

        hash_result_script_address = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.hash_result_script.get_taproot_address(
            self.destroyed_public_key
        )
        hash_result_signature = self.private_key.sign_taproot_input(
            bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.hash_result_tx,
            0,
            [hash_result_script_address.to_script_pub_key()],
            [funding_result_output_amount],
            script_path=True,
            tapleaf_script=bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.hash_result_script,
            sighash=TAPROOT_SIGHASH_ALL,
            tweak=False,
        )

        trigger_protocol_script_address = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_protocol_scripts_list.get_taproot_address(
            self.destroyed_public_key
        )
        trigger_protocol_script = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_protocol_scripts_list[
            bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_protocol_index()
        ]
        trigger_protocol_signature = self.private_key.sign_taproot_input(
            bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_protocol_tx,
            0,
            [trigger_protocol_script_address.to_script_pub_key()],
            [
                funding_result_output_amount
                - bitvmx_protocol_setup_properties_dto.step_fees_satoshis
            ],
            script_path=True,
            tapleaf_script=trigger_protocol_script,
            sighash=TAPROOT_SIGHASH_ALL,
            tweak=False,
        )

        search_hash_signatures = []
        search_choice_signatures = []
        for i in range(
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_wrong_step_search_iterations
        ):
            current_search_hash_tx = (
                bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.search_hash_tx_list[i]
            )
            current_search_hash_script_address = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.hash_search_scripts_list(
                iteration=i
            ).get_taproot_address(
                public_key=self.destroyed_public_key
            )
            current_search_hash_script = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.hash_search_scripts_list(
                iteration=i
            )[
                bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.hash_search_script_index()
            ]
            current_search_hash_signature = self.private_key.sign_taproot_input(
                current_search_hash_tx,
                0,
                [current_search_hash_script_address.to_script_pub_key()],
                [
                    funding_result_output_amount
                    - (2 * i + 2) * bitvmx_protocol_setup_properties_dto.step_fees_satoshis
                ],
                script_path=True,
                tapleaf_script=current_search_hash_script,
                sighash=TAPROOT_SIGHASH_ALL,
                tweak=False,
            )
            search_hash_signatures.append(current_search_hash_signature)

            current_search_choice_tx = (
                bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.search_choice_tx_list[
                    i
                ]
            )
            current_search_choice_script_address = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.choice_search_scripts_list(
                iteration=i
            ).get_taproot_address(
                public_key=self.destroyed_public_key
            )
            current_search_choice_script = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.choice_search_scripts_list(
                iteration=i
            )[
                bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.choice_search_script_index()
            ]
            current_search_choice_signature = self.private_key.sign_taproot_input(
                current_search_choice_tx,
                0,
                [current_search_choice_script_address.to_script_pub_key()],
                [
                    funding_result_output_amount
                    - (2 * i + 3) * bitvmx_protocol_setup_properties_dto.step_fees_satoshis
                ],
                script_path=True,
                tapleaf_script=current_search_choice_script,
                sighash=TAPROOT_SIGHASH_ALL,
                tweak=False,
            )
            search_choice_signatures.append(current_search_choice_signature)

        trace_script_address = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trace_script_list.get_taproot_address(
            self.destroyed_public_key
        )
        trace_script = (
            bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trace_script_list[
                bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trace_script_index()
            ]
        )
        trace_signature = self.private_key.sign_taproot_input(
            bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trace_tx,
            0,
            [trace_script_address.to_script_pub_key()],
            [
                funding_result_output_amount
                - (
                    2
                    * len(
                        bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.search_hash_tx_list
                    )
                    + 2
                )
                * bitvmx_protocol_setup_properties_dto.step_fees_satoshis
            ],
            script_path=True,
            tapleaf_script=trace_script,
            sighash=TAPROOT_SIGHASH_ALL,
            tweak=False,
        )

        trigger_trace_challenge_address = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_trace_challenge_address(
            self.destroyed_public_key
        )
        trigger_execution_challenge_signature = self.private_key.sign_taproot_input(
            bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_execution_challenge_tx,
            0,
            [trigger_trace_challenge_address.to_script_pub_key()],
            [
                funding_result_output_amount
                - (
                    2
                    * len(
                        bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.search_hash_tx_list
                    )
                    + 3
                )
                * bitvmx_protocol_setup_properties_dto.step_fees_satoshis
            ],
            script_path=True,
            tapleaf_script=bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_challenge_scripts[
                0
            ],
            sighash=TAPROOT_SIGHASH_ALL,
            tweak=False,
        )

        read_search_hash_signatures = []
        read_search_choice_signatures = []

        first_read_search_choice_tx = (
            bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.read_search_choice_tx_list[
                0
            ]
        )

        trigger_challenge_scripts_list = (
            bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_trace_challenge_scripts_list
        )
        choice_read_search_index = (
            bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_read_search_challenge_index()
        )

        first_read_search_choice_signature = self.private_key.sign_taproot_input(
            first_read_search_choice_tx,
            0,
            [trigger_trace_challenge_address.to_script_pub_key()],
            [
                funding_result_output_amount
                - (
                    2
                    * len(
                        bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.search_hash_tx_list
                    )
                    + 3
                )
                * bitvmx_protocol_setup_properties_dto.step_fees_satoshis
            ],
            script_path=True,
            tapleaf_script=trigger_challenge_scripts_list[choice_read_search_index],
            sighash=TAPROOT_SIGHASH_ALL,
            tweak=False,
        )
        read_search_choice_signatures.append(first_read_search_choice_signature)

        for i in range(
            len(bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.search_hash_tx_list)
            - 1
        ):
            # HASH
            current_read_search_hash_tx = bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.read_search_hash_tx_list[
                i
            ]
            current_read_search_hash_script_address = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.hash_read_search_scripts_list(
                iteration=i
            ).get_taproot_address(
                public_key=self.destroyed_public_key
            )

            current_read_search_hash_signature = self.private_key.sign_taproot_input(
                current_read_search_hash_tx,
                0,
                [current_read_search_hash_script_address.to_script_pub_key()],
                [
                    funding_result_output_amount
                    - (
                        2
                        + 2
                        * len(
                            bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.search_hash_tx_list
                        )
                        + 2
                        + 2 * i
                    )
                    * bitvmx_protocol_setup_properties_dto.step_fees_satoshis
                ],
                script_path=True,
                tapleaf_script=bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.hash_read_search_scripts_list(
                    iteration=i
                )[
                    bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.hash_read_search_script_index()
                ],
                sighash=TAPROOT_SIGHASH_ALL,
                tweak=False,
            )
            read_search_hash_signatures.append(current_read_search_hash_signature)

            # CHOICE
            current_read_search_choice_tx = bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.read_search_choice_tx_list[
                i + 1
            ]
            current_read_search_choice_script_list = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.choice_read_search_script_list(
                iteration=i + 1
            )
            current_read_search_choice_script_address = (
                current_read_search_choice_script_list.get_taproot_address(
                    public_key=self.destroyed_public_key
                )
            )
            current_read_search_choice_index = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.choice_read_search_script_index(
                iteration=i + 1
            )
            current_read_search_choice_script = current_read_search_choice_script_list[
                current_read_search_choice_index
            ]
            current_read_search_choice_signature = self.private_key.sign_taproot_input(
                current_read_search_choice_tx,
                0,
                [current_read_search_choice_script_address.to_script_pub_key()],
                [
                    funding_result_output_amount
                    - (
                        2
                        + 2
                        * len(
                            bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.search_hash_tx_list
                        )
                        + 3
                        + 2 * i
                    )
                    * bitvmx_protocol_setup_properties_dto.step_fees_satoshis
                ],
                script_path=True,
                tapleaf_script=current_read_search_choice_script,
                sighash=TAPROOT_SIGHASH_ALL,
                tweak=False,
            )
            read_search_choice_signatures.append(current_read_search_choice_signature)

        read_trace_script_address = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.read_trace_script_list.get_taproot_address(
            public_key=self.destroyed_public_key
        )

        read_trace_index = (
            bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.read_trace_script_index()
        )

        read_trace_signature = self.private_key.sign_taproot_input(
            bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.read_trace_tx,
            0,
            [read_trace_script_address.to_script_pub_key()],
            [
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
            ],
            script_path=True,
            tapleaf_script=bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.read_trace_script_list[
                read_trace_index
            ],
            sighash=TAPROOT_SIGHASH_ALL,
            tweak=False,
        )

        return BitVMXSignaturesDTO(
            hash_result_signature=hash_result_signature,
            trigger_protocol_signature=trigger_protocol_signature,
            search_hash_signatures=search_hash_signatures,
            search_choice_signatures=search_choice_signatures,
            trace_signature=trace_signature,
            trigger_execution_challenge_signature=trigger_execution_challenge_signature,
            read_search_hash_signatures=read_search_hash_signatures,
            read_search_choice_signatures=read_search_choice_signatures,
            read_trace_signature=read_trace_signature,
        )
