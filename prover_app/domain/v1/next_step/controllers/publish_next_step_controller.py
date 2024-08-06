import asyncio
import pickle
from typing import List

import httpx
from bitcoinutils.keys import PrivateKey

from bitvmx_protocol_library.transaction_generation.enums import TransactionProverStepType


async def _trigger_next_step_verifier(setup_uuid: str, verifier_list: List[str]):
    async with httpx.AsyncClient(timeout=1200.0) as client:
        call_verifiers_coroutines = []
        for verifier_host in verifier_list:
            url = f"{verifier_host}/next_step"
            headers = {"accept": "application/json", "Content-Type": "application/json"}

            # Be careful, this body is the verifier one -> app library
            call_verifiers_coroutines.append(
                asyncio.create_task(
                    client.post(url, headers=headers, json={"setup_uuid": setup_uuid})
                )
            )
        for coroutine in call_verifiers_coroutines:
            await coroutine


class PublishNextStepController:

    def __init__(
        self,
        transaction_published_service,
        publish_hash_transaction_service_class,
        publish_hash_search_transaction_service_class,
        publish_trace_transaction_service_class,
        execution_challenge_transaction_service_class,
    ):
        self.transaction_published_service = transaction_published_service
        self.publish_hash_transaction_service_class = publish_hash_transaction_service_class
        self.publish_hash_search_transaction_service_class = (
            publish_hash_search_transaction_service_class
        )
        self.publish_trace_transaction_service_class = publish_trace_transaction_service_class
        self.execution_challenge_transaction_service_class = (
            execution_challenge_transaction_service_class
        )

    def __call__(self, setup_uuid: str) -> TransactionProverStepType:
        with open(f"prover_files/{setup_uuid}/file_database.pkl", "rb") as f:
            protocol_dict = pickle.load(f)

        bitvmx_protocol_properties_dto = protocol_dict["bitvmx_protocol_properties_dto"]
        bitvmx_protocol_setup_properties_dto = protocol_dict["bitvmx_protocol_setup_properties_dto"]
        bitvmx_prover_winternitz_public_keys_dto = protocol_dict[
            "bitvmx_prover_winternitz_public_keys_dto"
        ]
        bitvmx_verifier_winternitz_public_keys_dto = protocol_dict[
            "bitvmx_verifier_winternitz_public_keys_dto"
        ]
        bitvmx_transactions_dto = protocol_dict["bitvmx_transactions_dto"]
        bitvmx_protocol_prover_private_dto = protocol_dict["bitvmx_protocol_prover_private_dto"]
        bitvmx_protocol_prover_dto = protocol_dict["bitvmx_protocol_prover_dto"]

        # prover_private_key = PrivateKey(b=bytes.fromhex(protocol_dict["prover_secret_key"]))
        wintertniz_private_key = PrivateKey(
            b=bytes.fromhex(bitvmx_protocol_prover_private_dto.winternitz_private_key)
        )

        if bitvmx_protocol_prover_dto.last_confirmed_step is None:
            publish_hash_transaction_service = self.publish_hash_transaction_service_class(
                wintertniz_private_key
            )
            last_confirmed_step_tx = publish_hash_transaction_service(
                setup_uuid=setup_uuid,
                bitvmx_protocol_properties_dto=bitvmx_protocol_properties_dto,
                bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
                bitvmx_transactions_dto=bitvmx_transactions_dto,
                bitvmx_protocol_prover_dto=bitvmx_protocol_prover_dto,
                bitvmx_prover_winternitz_public_keys_dto=bitvmx_prover_winternitz_public_keys_dto,
            )
            bitvmx_protocol_prover_dto.last_confirmed_step_tx_id = last_confirmed_step_tx.get_txid()
            bitvmx_protocol_prover_dto.last_confirmed_step = TransactionProverStepType.HASH_RESULT
        elif (
            bitvmx_protocol_prover_dto.last_confirmed_step == TransactionProverStepType.HASH_RESULT
            and self.transaction_published_service(
                bitvmx_transactions_dto.trigger_protocol_tx.get_txid()
            )
        ):
            publish_hash_search_transaction_service = (
                self.publish_hash_search_transaction_service_class(wintertniz_private_key)
            )
            last_confirmed_step_tx = publish_hash_search_transaction_service(
                protocol_dict=protocol_dict,
                bitvmx_transactions_dto=bitvmx_transactions_dto,
                iteration=0,
                setup_uuid=setup_uuid,
                bitvmx_protocol_properties_dto=bitvmx_protocol_properties_dto,
                bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
                bitvmx_prover_winternitz_public_keys_dto=bitvmx_prover_winternitz_public_keys_dto,
                bitvmx_verifier_winternitz_public_keys_dto=bitvmx_verifier_winternitz_public_keys_dto,
                bitvmx_protocol_prover_dto=bitvmx_protocol_prover_dto,
            )
            bitvmx_protocol_prover_dto.last_confirmed_step_tx_id = last_confirmed_step_tx.get_txid()
            bitvmx_protocol_prover_dto.last_confirmed_step = (
                TransactionProverStepType.SEARCH_STEP_HASH
            )
        elif (
            bitvmx_protocol_prover_dto.last_confirmed_step
            == TransactionProverStepType.SEARCH_STEP_HASH
        ):
            if (
                bitvmx_transactions_dto.search_hash_tx_list[-1].get_txid()
                == bitvmx_protocol_prover_dto.last_confirmed_step_tx_id
            ) and self.transaction_published_service(
                bitvmx_transactions_dto.search_choice_tx_list[-1].get_txid()
            ):
                publish_trace_transaction_service = self.publish_trace_transaction_service_class(
                    wintertniz_private_key
                )
                last_confirmed_step_tx = publish_trace_transaction_service(
                    protocol_dict=protocol_dict,
                    setup_uuid=setup_uuid,
                    bitvmx_transactions_dto=bitvmx_transactions_dto,
                    bitvmx_protocol_properties_dto=bitvmx_protocol_properties_dto,
                    bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
                    bitvmx_prover_winternitz_public_keys_dto=bitvmx_prover_winternitz_public_keys_dto,
                    bitvmx_verifier_winternitz_public_keys_dto=bitvmx_verifier_winternitz_public_keys_dto,
                    bitvmx_protocol_prover_dto=bitvmx_protocol_prover_dto,
                )
                bitvmx_protocol_prover_dto.last_confirmed_step_tx_id = (
                    last_confirmed_step_tx.get_txid()
                )
                bitvmx_protocol_prover_dto.last_confirmed_step = TransactionProverStepType.TRACE
            else:
                i = None
                for i in range(len(bitvmx_transactions_dto.search_hash_tx_list)):
                    if (
                        bitvmx_transactions_dto.search_hash_tx_list[i].get_txid()
                        == bitvmx_protocol_prover_dto.last_confirmed_step_tx_id
                    ):
                        break
                i += 1
                if i < len(
                    bitvmx_transactions_dto.search_choice_tx_list
                ) and self.transaction_published_service(
                    bitvmx_transactions_dto.search_choice_tx_list[i - 1].get_txid()
                ):
                    publish_hash_search_transaction_service = (
                        self.publish_hash_search_transaction_service_class(wintertniz_private_key)
                    )
                    last_confirmed_step_tx = publish_hash_search_transaction_service(
                        protocol_dict=protocol_dict,
                        bitvmx_transactions_dto=bitvmx_transactions_dto,
                        iteration=i,
                        setup_uuid=setup_uuid,
                        bitvmx_protocol_properties_dto=bitvmx_protocol_properties_dto,
                        bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
                        bitvmx_prover_winternitz_public_keys_dto=bitvmx_prover_winternitz_public_keys_dto,
                        bitvmx_verifier_winternitz_public_keys_dto=bitvmx_verifier_winternitz_public_keys_dto,
                        bitvmx_protocol_prover_dto=bitvmx_protocol_prover_dto,
                    )
                    bitvmx_protocol_prover_dto.last_confirmed_step_tx_id = (
                        last_confirmed_step_tx.get_txid()
                    )
                    bitvmx_protocol_prover_dto.last_confirmed_step = (
                        TransactionProverStepType.SEARCH_STEP_HASH
                    )
        elif bitvmx_protocol_prover_dto.last_confirmed_step == TransactionProverStepType.TRACE:
            # Here we should check which is the challenge that should be triggered
            if self.transaction_published_service(
                bitvmx_transactions_dto.trigger_execution_challenge_tx.get_txid()
            ):
                execution_challenge_transaction_service = (
                    self.execution_challenge_transaction_service_class()
                )
                last_confirmed_step_tx = execution_challenge_transaction_service(
                    protocol_dict=protocol_dict,
                    bitvmx_transactions_dto=bitvmx_transactions_dto,
                    bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
                    bitvmx_protocol_properties_dto=bitvmx_protocol_properties_dto,
                    bitvmx_prover_winternitz_public_keys_dto=bitvmx_prover_winternitz_public_keys_dto,
                    bitvmx_verifier_winternitz_public_keys_dto=bitvmx_verifier_winternitz_public_keys_dto,
                    bitvmx_protocol_prover_private_dto=bitvmx_protocol_prover_private_dto,
                    bitvmx_protocol_prover_dto=bitvmx_protocol_prover_dto,
                )
                bitvmx_protocol_prover_dto.last_confirmed_step_tx_id = (
                    last_confirmed_step_tx.get_txid()
                )
                bitvmx_protocol_prover_dto.last_confirmed_step = (
                    TransactionProverStepType.EXECUTION_CHALLENGE
                )

        with open(f"prover_files/{setup_uuid}/file_database.pkl", "wb") as f:
            pickle.dump(protocol_dict, f)

        if bitvmx_protocol_prover_dto.last_confirmed_step in [
            TransactionProverStepType.HASH_RESULT,
            TransactionProverStepType.SEARCH_STEP_HASH,
            TransactionProverStepType.TRACE,
        ]:
            asyncio.create_task(
                _trigger_next_step_verifier(
                    setup_uuid=setup_uuid,
                    verifier_list=bitvmx_protocol_setup_properties_dto.verifier_dict.values(),
                )
            )

        return bitvmx_protocol_prover_dto.last_confirmed_step
