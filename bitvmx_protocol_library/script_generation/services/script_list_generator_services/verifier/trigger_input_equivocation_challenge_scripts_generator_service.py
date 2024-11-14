from typing import List

from bitcoinutils.keys import PublicKey

from bitvmx_protocol_library.bitvmx_execution.services.execution_trace_generation_service import (
    ExecutionTraceGenerationService,
)
from bitvmx_protocol_library.bitvmx_execution.services.input_and_constant_addresses_generation_service import (
    InputAndConstantAddressesGenerationService,
)
from bitvmx_protocol_library.script_generation.entities.business_objects.bitcoin_script import (
    BitcoinScript,
)
from bitvmx_protocol_library.script_generation.entities.business_objects.bitcoin_script_list import (
    BitcoinScriptList,
)
from bitvmx_protocol_library.winternitz_keys_handling.scripts.verify_digit_signature_nibbles_service import (
    VerifyDigitSignatureNibblesService,
)


class TriggerInputEquivocationChallengeScriptsGeneratorService:
    def __init__(self):
        self.verify_input_nibble_message_from_public_keys = VerifyDigitSignatureNibblesService()
        self.input_and_constant_addresses_generation_service = (
            InputAndConstantAddressesGenerationService(
                instruction_commitment=ExecutionTraceGenerationService.commitment_file()
            )
        )

    def __call__(
        self,
        signature_public_keys: List[str],
        base_input_address: str,
        amount_of_input_words: int,
        address_public_keys: List[str],
        address_amount_of_nibbles: int,
        trace_value_public_keys: List[str],
        publish_hash_value_public_keys: List[List[str]],
        value_amount_of_nibbles: int,
        bits_per_digit_checksum: int,
    ) -> BitcoinScriptList:

        script_list = BitcoinScriptList()

        static_addresses = self.input_and_constant_addresses_generation_service(
            input_length=amount_of_input_words
        )

        int_base_input_address = int(static_addresses.input.address, 16)

        for i in range(amount_of_input_words):

            script = BitcoinScript()

            for signature_public_key in reversed(signature_public_keys):
                script.extend(
                    [PublicKey(hex_str=signature_public_key).to_x_only_hex(), "OP_CHECKSIGVERIFY"]
                )

            self.verify_input_nibble_message_from_public_keys(
                script=script,
                public_keys=address_public_keys,
                n0=address_amount_of_nibbles,
                bits_per_digit_checksum=bits_per_digit_checksum,
            )

            int_current_address = int_base_input_address + i * 4
            hex_current_address = hex(int_current_address)[2:].zfill(8)
            for letter in reversed(hex_current_address):
                script.append(int(letter, 16))
                script.append("OP_EQUALVERIFY")

            self.verify_input_nibble_message_from_public_keys(
                script=script,
                public_keys=publish_hash_value_public_keys[i],
                n0=value_amount_of_nibbles,
                bits_per_digit_checksum=bits_per_digit_checksum,
                to_alt_stack=True,
            )

            self.verify_input_nibble_message_from_public_keys(
                script=script,
                public_keys=trace_value_public_keys,
                n0=value_amount_of_nibbles,
                bits_per_digit_checksum=bits_per_digit_checksum,
            )

            script.append(0)
            for _ in range(value_amount_of_nibbles):
                script.extend([1, "OP_ROLL", "OP_FROMALTSTACK", "OP_EQUAL", "OP_ADD"])

            script.append(value_amount_of_nibbles)
            script.append("OP_LESSTHAN")

            script_list.append(script)

        return script_list
