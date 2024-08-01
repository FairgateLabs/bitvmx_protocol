import hashlib
import math
import os
import pickle
import secrets
import uuid
from typing import List

import requests
from bitcoinutils.keys import PrivateKey, PublicKey
from bitcoinutils.transactions import TxWitnessInput

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_properties_dto import (
    BitVMXProtocolPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_verifier_winternitz_public_keys_dto import (
    BitVMXVerifierWinternitzPublicKeysDTO,
)
from bitvmx_protocol_library.config import common_protocol_properties


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
    ):
        setup_uuid = str(uuid.uuid4())
        # This is hardcoded since it depends on the hashing function
        amount_of_nibbles_hash = 64
        # Computed parameters
        amount_of_wrong_step_search_hashes_per_iteration = 2**amount_of_bits_wrong_step_search - 1
        amount_of_wrong_step_search_iterations = math.ceil(
            math.ceil(math.log2(max_amount_of_steps)) / amount_of_bits_wrong_step_search
        )

        funding_tx = self.transaction_info_service(tx_id=funding_tx_id)
        initial_amount_of_satoshis = funding_tx.outputs[funding_index].value - step_fees_satoshis
        bitvmx_protocol_properties_dto = BitVMXProtocolPropertiesDTO(
            max_amount_of_steps=max_amount_of_steps,
            amount_of_bits_wrong_step_search=amount_of_bits_wrong_step_search,
            amount_of_bits_per_digit_checksum=amount_of_bits_per_digit_checksum,
        )

        bitvmx_protocol_setup_properties_dto = BitVMXProtocolSetupPropertiesDTO(
            setup_uuid=setup_uuid,
            funding_amount_of_satoshis=initial_amount_of_satoshis,
            step_fees_satoshis=step_fees_satoshis,
            funding_tx_id=funding_tx_id,
            funding_index=funding_index,
            verifier_list=verifier_list,
        )

        protocol_dict = {}
        protocol_dict["bitvmx_protocol_properties_dto"] = bitvmx_protocol_properties_dto
        protocol_dict["bitvmx_protocol_setup_properties_dto"] = bitvmx_protocol_setup_properties_dto
        protocol_dict["setup_uuid"] = setup_uuid
        protocol_dict["amount_of_trace_steps"] = (
            2**amount_of_bits_wrong_step_search
        ) ** amount_of_wrong_step_search_iterations
        protocol_dict["amount_of_bits_per_digit_checksum"] = amount_of_bits_per_digit_checksum
        protocol_dict["amount_of_wrong_step_search_iterations"] = (
            amount_of_wrong_step_search_iterations
        )
        protocol_dict["amount_of_bits_wrong_step_search"] = amount_of_bits_wrong_step_search
        protocol_dict["amount_of_wrong_step_search_hashes_per_iteration"] = (
            amount_of_wrong_step_search_hashes_per_iteration
        )
        protocol_dict["amount_of_nibbles_hash"] = amount_of_nibbles_hash
        protocol_dict["search_choices"] = []
        protocol_dict["published_hashes_dict"] = {}

        public_keys = []
        for verifier in verifier_list:
            url = f"{verifier}/setup"
            headers = {"accept": "application/json", "Content-Type": "application/json"}
            data = {"setup_uuid": setup_uuid, "network": common_protocol_properties.network.value}

            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                response_json = response.json()
                public_keys.append(response_json["public_key"])
            else:
                raise Exception("Some error ocurred with the setup call to the verifier")

        controlled_prover_public_key = controlled_prover_private_key.get_public_key()
        controlled_prover_address = controlled_prover_public_key.get_segwit_address().to_string()

        protocol_dict["controlled_prover_secret_key"] = (
            controlled_prover_private_key.to_bytes().hex()
        )
        protocol_dict["controlled_prover_public_key"] = controlled_prover_public_key.to_hex()
        protocol_dict["controlled_prover_address"] = controlled_prover_address

        destroyed_public_key = None
        seed_destroyed_public_key_hex = ""
        prover_private_key = PrivateKey(b=secrets.token_bytes(32))
        prover_public_key = prover_private_key.get_public_key()
        public_keys.append(prover_public_key.to_hex())
        while destroyed_public_key is None:
            try:
                seed_destroyed_public_key_hex = "".join(public_keys)
                destroyed_public_key_hex = hashlib.sha256(
                    bytes.fromhex(seed_destroyed_public_key_hex)
                ).hexdigest()
                destroyed_public_key = PublicKey(hex_str="02" + destroyed_public_key_hex)
                continue
            except IndexError:
                prover_private_key = PrivateKey(b=secrets.token_bytes(32))
                prover_public_key = prover_private_key.get_public_key()
                public_keys[-1] = prover_public_key.to_hex()

        protocol_dict["seed_destroyed_public_key_hex"] = seed_destroyed_public_key_hex
        protocol_dict["destroyed_public_key"] = destroyed_public_key.to_hex()
        protocol_dict["prover_secret_key"] = prover_private_key.to_bytes().hex()
        protocol_dict["prover_public_key"] = prover_public_key.to_hex()
        protocol_dict["public_keys"] = public_keys
        protocol_dict["network"] = common_protocol_properties.network

        generate_prover_public_keys_service = self.generate_prover_public_keys_service_class(
            prover_private_key
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

        # Think how to iterate all verifiers here -> Make a call per verifier
        # All verifiers should sign all transactions so they are sure there is not any of them lying
        url = f"{verifier_list[0]}/public_keys"
        headers = {"accept": "application/json", "Content-Type": "application/json"}
        data = {
            "setup_uuid": setup_uuid,
            "seed_destroyed_public_key_hex": seed_destroyed_public_key_hex,
            "prover_public_key": prover_public_key.to_hex(),
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
            bitvmx_prover_winternitz_public_keys_dto=bitvmx_prover_winternitz_public_keys_dto,
            bitvmx_verifier_winternitz_public_keys_dto=bitvmx_verifier_winternitz_public_keys_dto,
            signature_public_keys=protocol_dict["public_keys"],
        )

        protocol_dict["initial_amount_satoshis"] = initial_amount_of_satoshis
        protocol_dict["step_fees_satoshis"] = step_fees_satoshis

        # We need to know the origin of the funds or change the signature to only sign the output (it's possible and gives more flexibility)

        funding_result_output_amount = initial_amount_of_satoshis
        protocol_dict["funding_amount_satoshis"] = funding_result_output_amount

        # Transaction construction

        self.transaction_generator_from_public_keys_service(
            protocol_dict=protocol_dict,
            bitvmx_protocol_properties_dto=bitvmx_protocol_properties_dto,
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
            bitvmx_prover_winternitz_public_keys_dto=bitvmx_prover_winternitz_public_keys_dto,
            bitvmx_verifier_winternitz_public_keys_dto=bitvmx_verifier_winternitz_public_keys_dto,
        )

        # Signature computation

        generate_signatures_service = self.generate_signatures_service_class(
            prover_private_key, destroyed_public_key
        )
        signatures_dict = generate_signatures_service(
            protocol_dict=protocol_dict,
            bitvmx_bitcoin_scripts_dto=bitvmx_bitcoin_scripts_dto,
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
        )

        # Think how to iterate all verifiers here -> Maybe worth to make a call per verifier
        hash_result_signatures = [signatures_dict["hash_result_signature"]]
        search_hash_signatures = [
            [signature] for signature in signatures_dict["search_hash_signatures"]
        ]
        trace_signatures = [signatures_dict["trace_signature"]]
        # execution_challenge_signatures = [signatures_dict["execution_challenge_signature"]]
        for verifier in verifier_list:
            url = f"{verifier}/signatures"
            headers = {"accept": "application/json", "Content-Type": "application/json"}
            data = {
                "setup_uuid": setup_uuid,
                "trigger_protocol_signature": signatures_dict["trigger_protocol_signature"],
                "search_choice_signatures": signatures_dict["search_choice_signatures"],
                "trigger_execution_signature": signatures_dict["trigger_execution_signature"],
            }
            signatures_response = requests.post(url, headers=headers, json=data)
            if signatures_response.status_code != 200:
                raise Exception("Some error when exchanging the signatures")

            signatures_response_json = signatures_response.json()
            for j in range(len(signatures_response_json["verifier_search_hash_signatures"])):
                search_hash_signatures[j].append(
                    signatures_response_json["verifier_search_hash_signatures"][j]
                )

            hash_result_signatures.append(
                signatures_response_json["verifier_hash_result_signature"]
            )
            trace_signatures.append(signatures_response_json["verifier_trace_signature"])
            # execution_challenge_signatures.append(
            #     signatures_response_json["verifier_execution_challenge_signature"]
            # )

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
            destroyed_public_key
        )
        for i in range(len(protocol_dict["public_keys"]) - 1):
            verify_verifier_signatures_service(
                protocol_dict=protocol_dict,
                public_key=protocol_dict["public_keys"][i],
                hash_result_signature=protocol_dict["hash_result_signatures"][
                    len(protocol_dict["public_keys"]) - i - 2
                ],
                search_hash_signatures=[
                    signatures_list[len(protocol_dict["public_keys"]) - i - 2]
                    for signatures_list in protocol_dict["search_hash_signatures"]
                ],
                trace_signature=protocol_dict["trace_signatures"][
                    len(protocol_dict["public_keys"]) - i - 2
                ],
                bitvmx_bitcoin_scripts_dto=bitvmx_bitcoin_scripts_dto,
                bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
                # execution_challenge_signature=protocol_dict["execution_challenge_signatures"][
                #     len(protocol_dict["public_keys"]) - i - 2
                # ],
            )

        os.makedirs(f"prover_files/{setup_uuid}")

        with open(f"prover_files/{setup_uuid}/file_database.pkl", "xb") as f:
            pickle.dump(protocol_dict, f)

        #################################################################
        funding_tx = protocol_dict["funding_tx"]

        funding_sig = controlled_prover_private_key.sign_segwit_input(
            funding_tx,
            0,
            controlled_prover_public_key.get_address().to_script_pub_key(),
            initial_amount_of_satoshis + step_fees_satoshis,
        )

        funding_tx.witnesses.append(
            TxWitnessInput([funding_sig, controlled_prover_public_key.to_hex()])
        )

        self.broadcast_transaction_service(transaction=funding_tx.serialize())
        print("Funding transaction: " + funding_tx.get_txid())
        return setup_uuid
