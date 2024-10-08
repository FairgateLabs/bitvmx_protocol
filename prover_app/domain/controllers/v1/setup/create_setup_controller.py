import secrets
import uuid
from time import time
from typing import List

import requests
from bitcoinutils.keys import PrivateKey
from bitcoinutils.transactions import TxWitnessInput

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_properties_dto import (
    BitVMXProtocolPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_prover_dto import (
    BitVMXProtocolProverDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_prover_private_dto import (
    BitVMXProtocolProverPrivateDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_verifier_winternitz_public_keys_dto import (
    BitVMXVerifierWinternitzPublicKeysDTO,
)
from bitvmx_protocol_library.config import common_protocol_properties
from bitvmx_protocol_library.transaction_generation.entities.dtos.bitvmx_verifier_signatures_dto import (
    BitVMXVerifierSignaturesDTO,
)
from prover_app.domain.persistences.interfaces.bitvmx_protocol_prover_dto_persistence_interface import (
    BitVMXProtocolProverDTOPersistenceInterface,
)
from prover_app.domain.persistences.interfaces.bitvmx_protocol_prover_private_dto_persistence_interface import (
    BitVMXProtocolProverPrivateDTOPersistenceInterface,
)
from verifier_app.domain.persistences.interfaces.bitvmx_protocol_setup_properties_dto_persistence_interface import (
    BitVMXProtocolSetupPropertiesDTOPersistenceInterface,
)


class CreateSetupController:
    def __init__(
        self,
        broadcast_transaction_service,
        transaction_info_service,
        transaction_generator_from_public_keys_service,
        faucet_service,
        bitvmx_bitcoin_scripts_generator_service,
        generate_prover_public_keys_service_class,
        verify_verifier_signatures_service_class,
        generate_signatures_service_class,
        bitvmx_protocol_setup_properties_dto_persistence: BitVMXProtocolSetupPropertiesDTOPersistenceInterface,
        bitvmx_protocol_prover_private_dto_persistence: BitVMXProtocolProverPrivateDTOPersistenceInterface,
        bitvmx_protocol_prover_dto_persistence: BitVMXProtocolProverDTOPersistenceInterface,
    ):
        self.broadcast_transaction_service = broadcast_transaction_service
        self.transaction_info_service = transaction_info_service
        self.transaction_generator_from_public_keys_service = (
            transaction_generator_from_public_keys_service
        )
        self.faucet_service = faucet_service
        self.bitvmx_bitcoin_scripts_generator_service = bitvmx_bitcoin_scripts_generator_service
        self.generate_prover_public_keys_service_class = generate_prover_public_keys_service_class
        self.verify_verifier_signatures_service_class = verify_verifier_signatures_service_class
        self.generate_signatures_service_class = generate_signatures_service_class
        self.bitvmx_protocol_setup_properties_dto_persistence = (
            bitvmx_protocol_setup_properties_dto_persistence
        )
        self.bitvmx_protocol_prover_private_dto_persistence = (
            bitvmx_protocol_prover_private_dto_persistence
        )
        self.bitvmx_protocol_prover_dto_persistence = bitvmx_protocol_prover_dto_persistence

    async def __call__(
        self,
        max_amount_of_steps: int,
        amount_of_input_words: int,
        amount_of_bits_wrong_step_search: int,
        amount_of_bits_per_digit_checksum: int,
        verifier_list: List[str],
        controlled_prover_private_key: PrivateKey,
        funding_tx_id: str,
        funding_index: str,
        step_fees_satoshis: int,
        origin_of_funds_private_key: PrivateKey,
        prover_destination_address: str,
        prover_signature_private_key: str,
        prover_signature_public_key: str,
    ) -> str:
        setup_uuid = str(uuid.uuid4())
        prover_uuid = str(uuid.uuid4())
        init_time = time()

        funding_tx = self.transaction_info_service(tx_id=funding_tx_id)
        initial_amount_of_satoshis = funding_tx.outputs[funding_index].value - step_fees_satoshis
        bitvmx_protocol_properties_dto = BitVMXProtocolPropertiesDTO(
            max_amount_of_steps=max_amount_of_steps,
            amount_of_input_words=amount_of_input_words,
            amount_of_bits_wrong_step_search=amount_of_bits_wrong_step_search,
            amount_of_bits_per_digit_checksum=amount_of_bits_per_digit_checksum,
        )

        public_keys = []
        verifier_destroyed_public_key_hex = None
        verifier_signature_public_key_hex = None
        verifier_destination_address = None
        verifier_address_dict = {}
        signatures_public_keys_dict = {}
        for verifier in verifier_list:
            current_uuid = str(uuid.uuid4())
            verifier_address_dict[current_uuid] = verifier
            url = f"{verifier}/setup"
            headers = {"accept": "application/json", "Content-Type": "application/json"}
            data = {"setup_uuid": setup_uuid, "network": common_protocol_properties.network.value}

            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                response_json = response.json()
                verifier_destroyed_public_key_hex = response_json["public_key"]
                verifier_signature_public_key_hex = response_json["verifier_signature_public_key"]
                verifier_destination_address = response_json["verifier_destination_address"]
                public_keys.append(verifier_destroyed_public_key_hex)
                signatures_public_keys_dict[current_uuid] = verifier_destroyed_public_key_hex
            else:
                raise Exception("Some error ocurred with the setup call to the verifier")

        winternitz_private_key = PrivateKey(b=secrets.token_bytes(32))

        unspendable_public_key = None
        seed_unspendable_public_key = ""
        prover_destroyed_private_key = PrivateKey(b=secrets.token_bytes(32))
        prover_destroyed_public_key = prover_destroyed_private_key.get_public_key()
        public_keys.append(prover_destroyed_public_key.to_hex())
        while unspendable_public_key is None:
            try:
                seed_unspendable_public_key = "".join(public_keys)
                unspendable_public_key = (
                    BitVMXProtocolSetupPropertiesDTO.unspendable_public_key_from_seed(
                        seed_unspendable_public_key=seed_unspendable_public_key
                    )
                )
                continue
            except IndexError:
                prover_destroyed_private_key = PrivateKey(b=secrets.token_bytes(32))
                prover_destroyed_public_key = prover_destroyed_private_key.get_public_key()
                public_keys[-1] = prover_destroyed_public_key.to_hex()

        generate_prover_public_keys_service = self.generate_prover_public_keys_service_class(
            winternitz_private_key
        )
        print("Public keys generated: " + str(time() - init_time))
        bitvmx_prover_winternitz_public_keys_dto = generate_prover_public_keys_service(
            bitvmx_protocol_properties_dto=bitvmx_protocol_properties_dto,
        )

        print("Funding tx: " + funding_tx_id)

        bitvmx_protocol_setup_properties_dto = BitVMXProtocolSetupPropertiesDTO(
            setup_uuid=setup_uuid,
            uuid=prover_uuid,
            funding_amount_of_satoshis=initial_amount_of_satoshis,
            step_fees_satoshis=step_fees_satoshis,
            funding_tx_id=funding_tx_id,
            funding_index=funding_index,
            verifier_address_dict=verifier_address_dict,
            prover_destination_address=prover_destination_address,
            prover_signature_public_key=prover_signature_public_key,
            verifier_signature_public_key=verifier_signature_public_key_hex,
            verifier_destination_address=verifier_destination_address,
            seed_unspendable_public_key=seed_unspendable_public_key,
            prover_destroyed_public_key=prover_destroyed_private_key.get_public_key().to_hex(),
            verifier_destroyed_public_key=verifier_destroyed_public_key_hex,
            bitvmx_protocol_properties_dto=bitvmx_protocol_properties_dto,
            bitvmx_prover_winternitz_public_keys_dto=bitvmx_prover_winternitz_public_keys_dto,
        )

        verifier_public_keys_dict = {}

        # Think how to iterate all verifiers here -> Make a call per verifier
        # All verifiers should sign all transactions so they are sure there is not any of them lying
        for verifier_uuid, verifier_value in verifier_address_dict.items():
            url = f"{verifier_value}/public_keys"
            headers = {"accept": "application/json", "Content-Type": "application/json"}
            data = {
                "bitvmx_protocol_setup_properties_dto": bitvmx_protocol_setup_properties_dto.dict(),
            }

            public_keys_response = requests.post(url, headers=headers, json=data)
            if public_keys_response.status_code != 200:
                raise Exception("Some error with the public keys verifier call")
            public_keys_response_json = public_keys_response.json()

            verifier_public_keys_dict[verifier_uuid] = public_keys_response_json[
                "verifier_public_key"
            ]
            # We need to put a dict here
            bitvmx_protocol_setup_properties_dto.bitvmx_verifier_winternitz_public_keys_dto = (
                BitVMXVerifierWinternitzPublicKeysDTO(
                    **public_keys_response_json["bitvmx_verifier_winternitz_public_keys_dto"]
                )
            )
        print("Verifier public keys generated: " + str(time() - init_time))
        # Scripts building #

        # One call per verifier should be done
        bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto = (
            self.bitvmx_bitcoin_scripts_generator_service(
                bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
            )
        )
        print("Bitcoin scripts generated: " + str(time() - init_time))

        # We need to know the origin of the funds or change the signature to only sign the output (it's possible and gives more flexibility)

        # Transaction construction

        # One call per verifier should be done
        bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto = (
            self.transaction_generator_from_public_keys_service(
                bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
            )
        )
        print("Transactions built: " + str(time() - init_time))
        # Signature computation

        # One call per verifier should be done
        generate_signatures_service = self.generate_signatures_service_class(
            private_key=prover_destroyed_private_key, destroyed_public_key=unspendable_public_key
        )
        bitvmx_signatures_dto = generate_signatures_service(
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
        )
        print("Signatures generated: " + str(time() - init_time))
        hash_result_signatures = [bitvmx_signatures_dto.hash_result_signature]
        search_hash_signatures = [
            [signature] for signature in bitvmx_signatures_dto.search_hash_signatures
        ]
        trace_signatures = [bitvmx_signatures_dto.trace_signature]
        # execution_challenge_signatures = [signatures_dict["execution_challenge_signature"]]
        # At this stage, we need to add a GET call to compute the verifiers signatures for the other ones protocols
        verifier_signatures_dto_dict = {}
        for verifier_uuid, verifier_value in verifier_address_dict.items():
            url = f"{verifier_value}/signatures"
            headers = {"accept": "application/json", "Content-Type": "application/json"}
            data = {
                "setup_uuid": setup_uuid,
                "prover_signatures_dto": bitvmx_signatures_dto.prover_signatures_dto.model_dump(),
            }
            signatures_response = requests.post(url, headers=headers, json=data)
            if signatures_response.status_code != 200:
                raise Exception("Some error when exchanging the signatures")

            signatures_response_json = signatures_response.json()
            bitvmx_verifier_signatures_dto = BitVMXVerifierSignaturesDTO(
                **signatures_response_json["verifier_signatures_dto"]
            )

            for j in range(len(bitvmx_verifier_signatures_dto.search_hash_signatures)):
                search_hash_signatures[j].append(
                    bitvmx_verifier_signatures_dto.search_hash_signatures[j]
                )

            hash_result_signatures.append(bitvmx_verifier_signatures_dto.hash_result_signature)
            trace_signatures.append(bitvmx_verifier_signatures_dto.trace_signature)
            verifier_signatures_dto_dict[verifier_uuid] = bitvmx_verifier_signatures_dto
        print("Verifier signatures sent: " + str(time() - init_time))
        hash_result_signatures.reverse()
        for signature_list in search_hash_signatures:
            signature_list.reverse()
        trace_signatures.reverse()
        # execution_challenge_signatures.reverse()

        prover_signatures_dto = bitvmx_signatures_dto.verifier_signatures_dto
        bitvmx_protocol_prover_dto = BitVMXProtocolProverDTO(
            prover_public_key=prover_destroyed_public_key.to_hex(),
            verifier_public_keys=verifier_public_keys_dict,
            prover_signatures_dto=prover_signatures_dto,
            verifier_signatures_dtos=verifier_signatures_dto_dict,
        )

        verify_verifier_signatures_service = self.verify_verifier_signatures_service_class(
            unspendable_public_key=unspendable_public_key
        )
        for i in range(len(bitvmx_protocol_setup_properties_dto.signature_public_keys) - 1):
            verify_verifier_signatures_service(
                public_key=bitvmx_protocol_setup_properties_dto.signature_public_keys[i],
                hash_result_signature=bitvmx_verifier_signatures_dto.hash_result_signature,
                search_hash_signatures=bitvmx_verifier_signatures_dto.search_hash_signatures,
                trace_signature=bitvmx_verifier_signatures_dto.trace_signature,
                read_trace_signature=bitvmx_verifier_signatures_dto.read_trace_signature,
                read_search_hash_signatures=bitvmx_verifier_signatures_dto.read_search_hash_signatures,
                bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
            )

        bitvmx_protocol_prover_private_dto = BitVMXProtocolProverPrivateDTO(
            winternitz_private_key=winternitz_private_key.to_bytes().hex(),
            prover_signature_private_key=prover_signature_private_key,
        )

        self.bitvmx_protocol_setup_properties_dto_persistence.create(
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto
        )
        self.bitvmx_protocol_prover_private_dto_persistence.create(
            setup_uuid=setup_uuid,
            bitvmx_protocol_prover_private_dto=bitvmx_protocol_prover_private_dto,
        )
        self.bitvmx_protocol_prover_dto_persistence.create(
            setup_uuid=setup_uuid, bitvmx_protocol_prover_dto=bitvmx_protocol_prover_dto
        )

        #################################################################

        origin_of_funds_public_key = origin_of_funds_private_key.get_public_key()

        funding_sig = origin_of_funds_private_key.sign_segwit_input(
            bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.funding_tx,
            0,
            origin_of_funds_public_key.get_address().to_script_pub_key(),
            initial_amount_of_satoshis + step_fees_satoshis,
        )

        bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.funding_tx.witnesses.append(
            TxWitnessInput([funding_sig, origin_of_funds_public_key.to_hex()])
        )

        self.broadcast_transaction_service(
            transaction=bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.funding_tx.serialize()
        )
        print(
            "Funding transaction: "
            + bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.funding_tx.get_txid()
        )
        return setup_uuid
