import os
import pickle
import secrets
import uuid
from typing import List

import requests
from bitcoinutils.keys import PrivateKey
from bitcoinutils.transactions import TxWitnessInput

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_properties_dto import (
    BitVMXProtocolPropertiesDTO,
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

    async def __call__(
        self,
        max_amount_of_steps: int,
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

        funding_tx = self.transaction_info_service(tx_id=funding_tx_id)
        initial_amount_of_satoshis = funding_tx.outputs[funding_index].value - step_fees_satoshis
        bitvmx_protocol_properties_dto = BitVMXProtocolPropertiesDTO(
            max_amount_of_steps=max_amount_of_steps,
            amount_of_bits_wrong_step_search=amount_of_bits_wrong_step_search,
            amount_of_bits_per_digit_checksum=amount_of_bits_per_digit_checksum,
        )

        protocol_dict = {}
        protocol_dict["bitvmx_protocol_properties_dto"] = bitvmx_protocol_properties_dto

        protocol_dict["search_choices"] = []
        protocol_dict["published_hashes_dict"] = {}

        public_keys = []
        verifier_destroyed_public_key_hex = None
        verifier_dict = {}
        for verifier in verifier_list:
            current_uuid = str(uuid.uuid4())
            verifier_dict[current_uuid] = verifier
            url = f"{verifier}/setup"
            headers = {"accept": "application/json", "Content-Type": "application/json"}
            data = {"setup_uuid": setup_uuid, "network": common_protocol_properties.network.value}

            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                response_json = response.json()
                verifier_destroyed_public_key_hex = response_json["public_key"]
                public_keys.append(verifier_destroyed_public_key_hex)
            else:
                raise Exception("Some error ocurred with the setup call to the verifier")

        controlled_prover_public_key = controlled_prover_private_key.get_public_key()
        controlled_prover_address = controlled_prover_public_key.get_segwit_address().to_string()

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

        bitvmx_prover_winternitz_public_keys_dto = generate_prover_public_keys_service(
            bitvmx_protocol_properties_dto=bitvmx_protocol_properties_dto,
        )

        protocol_dict["bitvmx_prover_winternitz_public_keys_dto"] = (
            bitvmx_prover_winternitz_public_keys_dto
        )

        protocol_dict["funds_tx_id"] = funding_tx_id
        protocol_dict["funds_index"] = funding_index

        print("Funding tx: " + funding_tx_id)

        bitvmx_protocol_setup_properties_dto = BitVMXProtocolSetupPropertiesDTO(
            setup_uuid=setup_uuid,
            uuid=prover_uuid,
            funding_amount_of_satoshis=initial_amount_of_satoshis,
            step_fees_satoshis=step_fees_satoshis,
            funding_tx_id=funding_tx_id,
            funding_index=funding_index,
            verifier_dict=verifier_dict,
            prover_destination_address=prover_destination_address,
            prover_signature_public_key=prover_signature_public_key,
            seed_unspendable_public_key=seed_unspendable_public_key,
            prover_destroyed_public_key=prover_destroyed_private_key.get_public_key().to_hex(),
            verifier_destroyed_public_key=verifier_destroyed_public_key_hex,
        )
        protocol_dict["bitvmx_protocol_setup_properties_dto"] = bitvmx_protocol_setup_properties_dto

        # Think how to iterate all verifiers here -> Make a call per verifier
        # All verifiers should sign all transactions so they are sure there is not any of them lying
        url = f"{list(verifier_dict.values())[0]}/public_keys"
        headers = {"accept": "application/json", "Content-Type": "application/json"}
        data = {
            "setup_uuid": setup_uuid,
            "bitvmx_prover_winternitz_public_keys_dto": bitvmx_prover_winternitz_public_keys_dto.dict(),
            "bitvmx_protocol_setup_properties_dto": bitvmx_protocol_setup_properties_dto.dict(),
            "bitvmx_protocol_properties_dto": bitvmx_protocol_properties_dto.dict(),
            "controlled_prover_address": controlled_prover_address,
        }

        public_keys_response = requests.post(url, headers=headers, json=data)
        if public_keys_response.status_code != 200:
            raise Exception("Some error with the public keys verifier call")
        public_keys_response_json = public_keys_response.json()

        bitvmx_verifier_winternitz_public_keys_dto = BitVMXVerifierWinternitzPublicKeysDTO(
            **public_keys_response_json["bitvmx_verifier_winternitz_public_keys_dto"]
        )

        protocol_dict["bitvmx_verifier_winternitz_public_keys_dto"] = (
            bitvmx_verifier_winternitz_public_keys_dto
        )

        verifier_public_key = public_keys_response_json["verifier_public_key"]
        protocol_dict["verifier_public_key"] = verifier_public_key

        ## Scripts building ##

        bitvmx_bitcoin_scripts_dto = self.bitvmx_bitcoin_scripts_generator_service(
            bitvmx_protocol_properties_dto=bitvmx_protocol_properties_dto,
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
            bitvmx_prover_winternitz_public_keys_dto=bitvmx_prover_winternitz_public_keys_dto,
            bitvmx_verifier_winternitz_public_keys_dto=bitvmx_verifier_winternitz_public_keys_dto,
            signature_public_keys=bitvmx_protocol_setup_properties_dto.signature_public_keys,
        )

        # We need to know the origin of the funds or change the signature to only sign the output (it's possible and gives more flexibility)

        # Transaction construction
        bitvmx_transactions_dto = self.transaction_generator_from_public_keys_service(
            protocol_dict=protocol_dict,
            bitvmx_protocol_properties_dto=bitvmx_protocol_properties_dto,
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
            bitvmx_prover_winternitz_public_keys_dto=bitvmx_prover_winternitz_public_keys_dto,
            bitvmx_verifier_winternitz_public_keys_dto=bitvmx_verifier_winternitz_public_keys_dto,
        )

        protocol_dict["bitvmx_transactions_dto"] = bitvmx_transactions_dto

        # Signature computation
        generate_signatures_service = self.generate_signatures_service_class(
            private_key=prover_destroyed_private_key, destroyed_public_key=unspendable_public_key
        )
        bitvmx_signatures_dto = generate_signatures_service(
            bitvmx_transactions_dto=bitvmx_transactions_dto,
            bitvmx_bitcoin_scripts_dto=bitvmx_bitcoin_scripts_dto,
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
        )

        # Think how to iterate all verifiers here -> Maybe worth to make a call per verifier
        hash_result_signatures = [bitvmx_signatures_dto.hash_result_signature]
        search_hash_signatures = [
            [signature] for signature in bitvmx_signatures_dto.search_hash_signatures
        ]
        trace_signatures = [bitvmx_signatures_dto.trace_signature]
        # execution_challenge_signatures = [signatures_dict["execution_challenge_signature"]]
        for verifier_uuid, verifier_value in verifier_dict.items():
            url = f"{verifier_value}/signatures"
            headers = {"accept": "application/json", "Content-Type": "application/json"}
            data = {
                "setup_uuid": setup_uuid,
                "prover_signatures": bitvmx_signatures_dto.prover_signatures.model_dump(),
            }
            signatures_response = requests.post(url, headers=headers, json=data)
            if signatures_response.status_code != 200:
                raise Exception("Some error when exchanging the signatures")

            signatures_response_json = signatures_response.json()
            bitvmx_verifier_signatures_dto = BitVMXVerifierSignaturesDTO(
                **signatures_response_json["verifier_signatures"]
            )
            protocol_dict["bitvmx_verifier_signatures_dto"] = bitvmx_verifier_signatures_dto
            for j in range(len(bitvmx_verifier_signatures_dto.search_hash_signatures)):
                search_hash_signatures[j].append(
                    bitvmx_verifier_signatures_dto.search_hash_signatures[j]
                )

            hash_result_signatures.append(bitvmx_verifier_signatures_dto.hash_result_signature)
            trace_signatures.append(bitvmx_verifier_signatures_dto.trace_signature)

        hash_result_signatures.reverse()
        for signature_list in search_hash_signatures:
            signature_list.reverse()
        trace_signatures.reverse()
        # execution_challenge_signatures.reverse()

        protocol_dict["hash_result_signatures"] = hash_result_signatures
        protocol_dict["search_hash_signatures"] = search_hash_signatures
        protocol_dict["trace_signatures"] = trace_signatures
        # protocol_dict["execution_challenge_signatures"] = execution_challenge_signatures

        verify_verifier_signatures_service = self.verify_verifier_signatures_service_class(
            unspendable_public_key=unspendable_public_key
        )
        for i in range(len(bitvmx_protocol_setup_properties_dto.signature_public_keys) - 1):
            verify_verifier_signatures_service(
                public_key=bitvmx_protocol_setup_properties_dto.signature_public_keys[i],
                hash_result_signature=protocol_dict["hash_result_signatures"][
                    len(bitvmx_protocol_setup_properties_dto.signature_public_keys) - i - 2
                ],
                search_hash_signatures=[
                    signatures_list[
                        len(bitvmx_protocol_setup_properties_dto.signature_public_keys) - i - 2
                    ]
                    for signatures_list in protocol_dict["search_hash_signatures"]
                ],
                trace_signature=protocol_dict["trace_signatures"][
                    len(bitvmx_protocol_setup_properties_dto.signature_public_keys) - i - 2
                ],
                bitvmx_transactions_dto=bitvmx_transactions_dto,
                bitvmx_bitcoin_scripts_dto=bitvmx_bitcoin_scripts_dto,
                bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
                # execution_challenge_signature=protocol_dict["execution_challenge_signatures"][
                #     len(protocol_dict["public_keys"]) - i - 2
                # ],
            )

        protocol_dict["bitvmx_protocol_prover_private_dto"] = BitVMXProtocolProverPrivateDTO(
            winternitz_private_key=winternitz_private_key.to_bytes().hex(),
            prover_signature_private_key=prover_signature_private_key,
        )

        os.makedirs(f"prover_files/{setup_uuid}")

        with open(f"prover_files/{setup_uuid}/file_database.pkl", "xb") as f:
            pickle.dump(protocol_dict, f)

        #################################################################

        origin_of_funds_public_key = origin_of_funds_private_key.get_public_key()

        funding_sig = origin_of_funds_private_key.sign_segwit_input(
            bitvmx_transactions_dto.funding_tx,
            0,
            origin_of_funds_public_key.get_address().to_script_pub_key(),
            initial_amount_of_satoshis + step_fees_satoshis,
        )

        bitvmx_transactions_dto.funding_tx.witnesses.append(
            TxWitnessInput([funding_sig, origin_of_funds_public_key.to_hex()])
        )

        self.broadcast_transaction_service(
            transaction=bitvmx_transactions_dto.funding_tx.serialize()
        )
        print("Funding transaction: " + bitvmx_transactions_dto.funding_tx.get_txid())
        return setup_uuid
