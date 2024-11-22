import asyncio

import httpx
from bitcoinutils.keys import PrivateKey
from bitcoinutils.setup import get_network

from bitvmx_protocol_library.enums import BitcoinNetwork
from bitvmx_protocol_library.transaction_generation.enums import TransactionVerifierStepType
from blockchain_query_services.services.blockchain_query_services_dependency_injection import (
    transaction_info_service,
)
from verifier_app.domain.persistences.interfaces.bitvmx_protocol_setup_properties_dto_persistence_interface import (
    BitVMXProtocolSetupPropertiesDTOPersistenceInterface,
)
from verifier_app.domain.persistences.interfaces.bitvmx_protocol_verifier_dto_persistence_interface import (
    BitVMXProtocolVerifierDTOPersistenceInterface,
)
from verifier_app.domain.persistences.interfaces.bitvmx_protocol_verifier_private_dto_persistence_interface import (
    BitVMXProtocolVerifierPrivateDTOPersistenceInterface,
)


async def _trigger_next_step_prover(setup_uuid: str, prover_host: str):
    prover_host = prover_host
    url = f"{prover_host}/next_step"
    headers = {"accept": "application/json", "Content-Type": "application/json"}

    # Be careful, this body is the prover one -> app library
    # Make the POST request
    async with httpx.AsyncClient(timeout=3000.0) as client:
        await client.post(url, headers=headers, json={"setup_uuid": setup_uuid})


class PublishNextStepController:

    def __init__(
        self,
        verifier_challenge_detection_service,
        verifier_read_challenge_detection_service,
        trigger_protocol_transaction_service_class,
        publish_choice_search_transaction_service_class,
        publish_choice_read_search_transaction_service_class,
        trigger_read_search_equivocation_transaction_service_class,
        protocol_properties,
        common_protocol_properties,
        bitvmx_protocol_verifier_private_dto_persistence: BitVMXProtocolVerifierPrivateDTOPersistenceInterface,
        bitvmx_protocol_setup_properties_dto_persistence: BitVMXProtocolSetupPropertiesDTOPersistenceInterface,
        bitvmx_protocol_verifier_dto_persistence: BitVMXProtocolVerifierDTOPersistenceInterface,
    ):
        self.verifier_challenge_detection_service = verifier_challenge_detection_service
        self.verifier_read_challenge_detection_service = verifier_read_challenge_detection_service
        self.trigger_protocol_transaction_service_class = trigger_protocol_transaction_service_class
        self.publish_choice_search_transaction_service_class = (
            publish_choice_search_transaction_service_class
        )
        self.publish_choice_read_search_transaction_service_class = (
            publish_choice_read_search_transaction_service_class
        )
        self.trigger_read_search_equivocation_transaction_service_class = (
            trigger_read_search_equivocation_transaction_service_class
        )
        self.protocol_properties = protocol_properties
        self.common_protocol_properties = common_protocol_properties
        self.bitvmx_protocol_verifier_private_dto_persistence = (
            bitvmx_protocol_verifier_private_dto_persistence
        )
        self.bitvmx_protocol_setup_properties_dto_persistence = (
            bitvmx_protocol_setup_properties_dto_persistence
        )
        self.bitvmx_protocol_verifier_dto_persistence = bitvmx_protocol_verifier_dto_persistence

    async def __call__(self, setup_uuid: str):
        if self.common_protocol_properties.network == BitcoinNetwork.MUTINYNET:
            assert get_network() == "testnet"
        else:
            assert get_network() == self.common_protocol_properties.network.value

        bitvmx_protocol_setup_properties_dto = (
            self.bitvmx_protocol_setup_properties_dto_persistence.get(setup_uuid=setup_uuid)
        )

        bitvmx_protocol_verifier_dto = self.bitvmx_protocol_verifier_dto_persistence.get(
            setup_uuid=setup_uuid
        )
        bitvmx_protocol_verifier_private_dto = (
            self.bitvmx_protocol_verifier_private_dto_persistence.get(setup_uuid=setup_uuid)
        )

        if bitvmx_protocol_verifier_dto.last_confirmed_step is None and (
            hash_result_transaction := transaction_info_service(
                bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.hash_result_tx.get_txid()
            )
        ):
            winternitz_verifier_private_key = PrivateKey(
                b=bytes.fromhex(bitvmx_protocol_verifier_private_dto.winternitz_private_key)
            )
            trigger_protocol_transaction_service = self.trigger_protocol_transaction_service_class(
                verifier_private_key=winternitz_verifier_private_key
            )
            last_confirmed_step_tx = trigger_protocol_transaction_service(
                hash_result_transaction=hash_result_transaction,
                bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
                bitvmx_protocol_verifier_dto=bitvmx_protocol_verifier_dto,
            )
            bitvmx_protocol_verifier_dto.last_confirmed_step_tx_id = (
                last_confirmed_step_tx.get_txid()
            )
            bitvmx_protocol_verifier_dto.last_confirmed_step = (
                TransactionVerifierStepType.TRIGGER_PROTOCOL
            )
        elif (
            bitvmx_protocol_verifier_dto.last_confirmed_step
            is TransactionVerifierStepType.TRIGGER_PROTOCOL
        ):
            # VERIFY THE PREVIOUS STEP #
            winternitz_verifier_private_key = PrivateKey(
                b=bytes.fromhex(bitvmx_protocol_verifier_private_dto.winternitz_private_key)
            )
            i = 0
            publish_choice_search_transaction_service = (
                self.publish_choice_search_transaction_service_class(
                    winternitz_verifier_private_key
                )
            )
            last_confirmed_step_tx = publish_choice_search_transaction_service(
                iteration=i,
                bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
                bitvmx_protocol_verifier_dto=bitvmx_protocol_verifier_dto,
            )
            bitvmx_protocol_verifier_dto.last_confirmed_step_tx_id = (
                last_confirmed_step_tx.get_txid()
            )
            bitvmx_protocol_verifier_dto.last_confirmed_step = (
                TransactionVerifierStepType.SEARCH_STEP_CHOICE
            )
        elif (
            bitvmx_protocol_verifier_dto.last_confirmed_step
            is TransactionVerifierStepType.READ_SEARCH_STEP_CHOICE
            and bitvmx_protocol_verifier_dto.last_confirmed_step_tx_id
            == bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.read_search_choice_tx_list[
                -1
            ].get_txid()
        ):
            read_challenge_transaction_service, transaction_step_type = (
                self.verifier_read_challenge_detection_service(
                    bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
                    bitvmx_protocol_verifier_dto=bitvmx_protocol_verifier_dto,
                )
            )
            if read_challenge_transaction_service is not None and transaction_step_type is not None:
                winternitz_verifier_private_key = PrivateKey(
                    b=bytes.fromhex(bitvmx_protocol_verifier_private_dto.winternitz_private_key)
                )
                trigger_read_challenge_transaction_service = read_challenge_transaction_service(
                    winternitz_verifier_private_key
                )
                last_confirmed_step_tx = trigger_read_challenge_transaction_service(
                    bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
                    bitvmx_protocol_verifier_private_dto=bitvmx_protocol_verifier_private_dto,
                    bitvmx_protocol_verifier_dto=bitvmx_protocol_verifier_dto,
                )
                bitvmx_protocol_verifier_dto.last_confirmed_step_tx_id = (
                    last_confirmed_step_tx.get_txid()
                )
                bitvmx_protocol_verifier_dto.last_confirmed_step = transaction_step_type
        elif (
            bitvmx_protocol_verifier_dto.last_confirmed_step
            is TransactionVerifierStepType.READ_SEARCH_STEP_CHOICE
        ):
            winternitz_verifier_private_key = PrivateKey(
                b=bytes.fromhex(bitvmx_protocol_verifier_private_dto.winternitz_private_key)
            )
            publish_choice_read_search_transaction_service = (
                self.publish_choice_read_search_transaction_service_class(
                    winternitz_verifier_private_key
                )
            )

            target_step, new_published_hashes_dict = (
                publish_choice_read_search_transaction_service.get_target_step(
                    bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
                    bitvmx_protocol_verifier_dto=bitvmx_protocol_verifier_dto,
                )
            )

            if target_step == -1:
                trigger_read_search_equivocation_transaction_service = (
                    self.trigger_read_search_equivocation_transaction_service_class()
                )
                last_confirmed_step_tx = trigger_read_search_equivocation_transaction_service(
                    bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
                    bitvmx_protocol_verifier_private_dto=bitvmx_protocol_verifier_private_dto,
                    bitvmx_protocol_verifier_dto=bitvmx_protocol_verifier_dto,
                )
                bitvmx_protocol_verifier_dto.last_confirmed_step_tx_id = (
                    last_confirmed_step_tx.get_txid()
                )
                bitvmx_protocol_verifier_dto.last_confirmed_step = (
                    TransactionVerifierStepType.TRIGGER_READ_SEARCH_EQUIVOCATION_CHALLENGE
                )
            elif target_step >= 0:
                last_confirmed_step_tx = publish_choice_read_search_transaction_service(
                    bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
                    bitvmx_protocol_verifier_private_dto=bitvmx_protocol_verifier_private_dto,
                    bitvmx_protocol_verifier_dto=bitvmx_protocol_verifier_dto,
                    target_step=target_step,
                    new_published_hashes_dict=new_published_hashes_dict,
                )
                bitvmx_protocol_verifier_dto.last_confirmed_step_tx_id = (
                    last_confirmed_step_tx.get_txid()
                )
                bitvmx_protocol_verifier_dto.last_confirmed_step = (
                    TransactionVerifierStepType.READ_SEARCH_STEP_CHOICE
                )
            else:
                raise Exception("Exception in target step not considered")
        elif (
            bitvmx_protocol_verifier_dto.last_confirmed_step
            is TransactionVerifierStepType.SEARCH_STEP_CHOICE
            and bitvmx_protocol_verifier_dto.last_confirmed_step_tx_id
            == bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.search_choice_tx_list[
                -1
            ].get_txid()
        ):
            challenge_transaction_service, transaction_step_type = (
                self.verifier_challenge_detection_service(
                    bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
                    bitvmx_protocol_verifier_dto=bitvmx_protocol_verifier_dto,
                )
            )
            if challenge_transaction_service is not None and transaction_step_type is not None:
                winternitz_verifier_private_key = PrivateKey(
                    b=bytes.fromhex(bitvmx_protocol_verifier_private_dto.winternitz_private_key)
                )
                trigger_challenge_transaction_service = challenge_transaction_service(
                    winternitz_verifier_private_key
                )
                last_confirmed_step_tx = trigger_challenge_transaction_service(
                    bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
                    bitvmx_protocol_verifier_private_dto=bitvmx_protocol_verifier_private_dto,
                    bitvmx_protocol_verifier_dto=bitvmx_protocol_verifier_dto,
                )
                bitvmx_protocol_verifier_dto.last_confirmed_step_tx_id = (
                    last_confirmed_step_tx.get_txid()
                )
                bitvmx_protocol_verifier_dto.last_confirmed_step = transaction_step_type
        elif (
            bitvmx_protocol_verifier_dto.last_confirmed_step
            is TransactionVerifierStepType.SEARCH_STEP_CHOICE
        ):
            # VERIFY THE PREVIOUS STEP #
            winternitz_verifier_private_key = PrivateKey(
                b=bytes.fromhex(bitvmx_protocol_verifier_private_dto.winternitz_private_key)
            )
            i = 0
            for i in range(
                len(
                    bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.search_choice_tx_list
                )
            ):
                if (
                    bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.search_choice_tx_list[
                        i
                    ].get_txid()
                    == bitvmx_protocol_verifier_dto.last_confirmed_step_tx_id
                ):
                    break
            i += 1
            if i < len(
                bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.search_choice_tx_list
            ):
                publish_choice_search_transaction_service = (
                    self.publish_choice_search_transaction_service_class(
                        winternitz_verifier_private_key
                    )
                )
                last_confirmed_step_tx = publish_choice_search_transaction_service(
                    bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
                    iteration=i,
                    bitvmx_protocol_verifier_dto=bitvmx_protocol_verifier_dto,
                )
                bitvmx_protocol_verifier_dto.last_confirmed_step_tx_id = (
                    last_confirmed_step_tx.get_txid()
                )
                bitvmx_protocol_verifier_dto.last_confirmed_step = (
                    TransactionVerifierStepType.SEARCH_STEP_CHOICE
                )

        if bitvmx_protocol_verifier_dto.last_confirmed_step in [
            TransactionVerifierStepType.TRIGGER_PROTOCOL,
            TransactionVerifierStepType.SEARCH_STEP_CHOICE,
            TransactionVerifierStepType.TRIGGER_EXECUTION_CHALLENGE,
            TransactionVerifierStepType.READ_SEARCH_STEP_CHOICE,
        ]:
            asyncio.create_task(
                _trigger_next_step_prover(
                    setup_uuid=setup_uuid, prover_host=self.protocol_properties.prover_host
                )
            )

        self.bitvmx_protocol_verifier_dto_persistence.update(
            setup_uuid=setup_uuid, bitvmx_protocol_verifier_dto=bitvmx_protocol_verifier_dto
        )

        return bitvmx_protocol_verifier_dto.last_confirmed_step
