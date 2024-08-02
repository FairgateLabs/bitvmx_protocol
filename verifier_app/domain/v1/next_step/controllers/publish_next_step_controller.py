import asyncio
import pickle

import httpx
from bitcoinutils.keys import PrivateKey
from bitcoinutils.setup import NETWORK

from bitvmx_protocol_library.enums import BitcoinNetwork
from bitvmx_protocol_library.transaction_generation.enums import TransactionVerifierStepType
from blockchain_query_services.services.blockchain_query_services_dependency_injection import (
    transaction_info_service,
)


async def _trigger_next_step_prover(setup_uuid: str, prover_host: str):
    prover_host = prover_host
    url = f"{prover_host}/next_step"
    headers = {"accept": "application/json", "Content-Type": "application/json"}

    # Be careful, this body is the prover one -> app library
    # Make the POST request
    async with httpx.AsyncClient(timeout=1200.0) as client:
        await client.post(url, headers=headers, json={"setup_uuid": setup_uuid})


class PublishNextStepController:

    def __init__(
        self,
        trigger_protocol_transaction_service,
        verifier_challenge_detection_service,
        publish_choice_search_transaction_service_class,
        protocol_properties,
    ):
        self.trigger_protocol_transaction_service = trigger_protocol_transaction_service
        self.verifier_challenge_detection_service = verifier_challenge_detection_service
        self.publish_choice_search_transaction_service_class = (
            publish_choice_search_transaction_service_class
        )
        self.protocol_properties = protocol_properties

    async def __call__(self, setup_uuid):
        with open(f"verifier_files/{setup_uuid}/file_database.pkl", "rb") as f:
            protocol_dict = pickle.load(f)
        if protocol_dict["network"] == BitcoinNetwork.MUTINYNET:
            assert NETWORK == "testnet"
        else:
            assert NETWORK == protocol_dict["network"].value
        last_confirmed_step = protocol_dict["last_confirmed_step"]
        last_confirmed_step_tx_id = protocol_dict["last_confirmed_step_tx_id"]

        bitvmx_protocol_properties_dto = protocol_dict["bitvmx_protocol_properties_dto"]
        bitvmx_protocol_setup_properties_dto = protocol_dict["bitvmx_protocol_setup_properties_dto"]
        bitvmx_prover_winternitz_public_keys_dto = protocol_dict[
            "bitvmx_prover_winternitz_public_keys_dto"
        ]
        bitvmx_verifier_winternitz_public_keys_dto = protocol_dict[
            "bitvmx_verifier_winternitz_public_keys_dto"
        ]
        bitvmx_transactions_dto = protocol_dict["bitvmx_transactions_dto"]

        if last_confirmed_step is None and (
            hash_result_transaction := transaction_info_service(
                bitvmx_transactions_dto.hash_result_tx.get_txid()
            )
        ):
            last_confirmed_step_tx = self.trigger_protocol_transaction_service(
                protocol_dict=protocol_dict,
                hash_result_transaction=hash_result_transaction,
                bitvmx_transactions_dto=bitvmx_transactions_dto,
                bitvmx_protocol_properties_dto=bitvmx_protocol_properties_dto,
                bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
            )
            last_confirmed_step_tx_id = last_confirmed_step_tx.get_txid()
            last_confirmed_step = TransactionVerifierStepType.TRIGGER_PROTOCOL
            protocol_dict["last_confirmed_step_tx_id"] = last_confirmed_step_tx_id
            protocol_dict["last_confirmed_step"] = last_confirmed_step
        elif last_confirmed_step is TransactionVerifierStepType.TRIGGER_PROTOCOL:
            ## VERIFY THE PREVIOUS STEP ##
            verifier_private_key = PrivateKey(
                b=bytes.fromhex(protocol_dict["verifier_private_key"])
            )
            i = 0
            publish_choice_search_transaction_service = (
                self.publish_choice_search_transaction_service_class(verifier_private_key)
            )
            last_confirmed_step_tx = publish_choice_search_transaction_service(
                protocol_dict=protocol_dict,
                iteration=i,
                bitvmx_transactions_dto=bitvmx_transactions_dto,
                bitvmx_protocol_properties_dto=bitvmx_protocol_properties_dto,
                bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
                bitvmx_prover_winternitz_public_keys_dto=bitvmx_prover_winternitz_public_keys_dto,
                bitvmx_verifier_winternitz_public_keys_dto=bitvmx_verifier_winternitz_public_keys_dto,
            )
            last_confirmed_step_tx_id = last_confirmed_step_tx.get_txid()
            last_confirmed_step = TransactionVerifierStepType.SEARCH_STEP_CHOICE
            protocol_dict["last_confirmed_step_tx_id"] = last_confirmed_step_tx_id
            protocol_dict["last_confirmed_step"] = last_confirmed_step
        elif (
            last_confirmed_step is TransactionVerifierStepType.SEARCH_STEP_CHOICE
            and last_confirmed_step_tx_id
            == bitvmx_transactions_dto.search_choice_tx_list[-1].get_txid()
        ):
            challenge_transaction_service, transaction_step_type = (
                self.verifier_challenge_detection_service(
                    protocol_dict=protocol_dict,
                    bitvmx_transactions_dto=bitvmx_transactions_dto,
                    bitvmx_protocol_properties_dto=bitvmx_protocol_properties_dto,
                    bitvmx_prover_winternitz_public_keys_dto=bitvmx_prover_winternitz_public_keys_dto,
                    bitvmx_verifier_winternitz_public_keys_dto=bitvmx_verifier_winternitz_public_keys_dto,
                )
            )
            # As of now, this only holds for single step challenges
            if challenge_transaction_service is not None and transaction_step_type is not None:
                verifier_private_key = PrivateKey(
                    b=bytes.fromhex(protocol_dict["verifier_private_key"])
                )
                trigger_challenge_transaction_service = challenge_transaction_service(
                    verifier_private_key
                )
                last_confirmed_step_tx = trigger_challenge_transaction_service(
                    protocol_dict=protocol_dict,
                    bitvmx_transactions_dto=bitvmx_transactions_dto,
                    bitvmx_protocol_properties_dto=bitvmx_protocol_properties_dto,
                    bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
                    bitvmx_prover_winternitz_public_keys_dto=bitvmx_prover_winternitz_public_keys_dto,
                    bitvmx_verifier_winternitz_public_keys_dto=bitvmx_verifier_winternitz_public_keys_dto,
                )
                last_confirmed_step_tx_id = last_confirmed_step_tx.get_txid()
                last_confirmed_step = transaction_step_type
                protocol_dict["last_confirmed_step_tx_id"] = last_confirmed_step_tx_id
                protocol_dict["last_confirmed_step"] = last_confirmed_step
        elif last_confirmed_step is TransactionVerifierStepType.SEARCH_STEP_CHOICE:
            ## VERIFY THE PREVIOUS STEP ##
            verifier_private_key = PrivateKey(
                b=bytes.fromhex(protocol_dict["verifier_private_key"])
            )
            i = 0
            for i in range(len(bitvmx_transactions_dto.search_choice_tx_list)):
                if (
                    bitvmx_transactions_dto.search_choice_tx_list[i].get_txid()
                    == protocol_dict["last_confirmed_step_tx_id"]
                ):
                    break
            i += 1
            if i < len(bitvmx_transactions_dto.search_choice_tx_list):
                publish_choice_search_transaction_service = (
                    self.publish_choice_search_transaction_service_class(verifier_private_key)
                )
                last_confirmed_step_tx = publish_choice_search_transaction_service(
                    protocol_dict=protocol_dict,
                    bitvmx_transactions_dto=bitvmx_transactions_dto,
                    bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
                    iteration=i,
                    bitvmx_protocol_properties_dto=bitvmx_protocol_properties_dto,
                    bitvmx_prover_winternitz_public_keys_dto=bitvmx_prover_winternitz_public_keys_dto,
                    bitvmx_verifier_winternitz_public_keys_dto=bitvmx_verifier_winternitz_public_keys_dto,
                )
                last_confirmed_step_tx_id = last_confirmed_step_tx.get_txid()
                last_confirmed_step = TransactionVerifierStepType.SEARCH_STEP_CHOICE
                protocol_dict["last_confirmed_step_tx_id"] = last_confirmed_step_tx_id
                protocol_dict["last_confirmed_step"] = last_confirmed_step

        if last_confirmed_step in [
            TransactionVerifierStepType.TRIGGER_PROTOCOL,
            TransactionVerifierStepType.SEARCH_STEP_CHOICE,
            TransactionVerifierStepType.TRIGGER_EXECUTION_CHALLENGE,
            TransactionVerifierStepType.TRIGGER_WRONG_HASH_CHALLENGE,
        ]:
            asyncio.create_task(
                _trigger_next_step_prover(
                    setup_uuid=setup_uuid, prover_host=self.protocol_properties.prover_host
                )
            )

        with open(f"verifier_files/{setup_uuid}/file_database.pkl", "wb") as f:
            pickle.dump(protocol_dict, f)

        return last_confirmed_step
