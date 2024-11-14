from typing import Dict, List

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


class TriggerConstantEquivocationChallengeScriptsGeneratorService:
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
        constant_memory_regions: Dict[str, str],
        address_public_keys: List[str],
        address_amount_of_nibbles: int,
        trace_value_public_keys: List[str],
        value_amount_of_nibbles: int,
        bits_per_digit_checksum: int,
    ) -> BitcoinScriptList:
        script_list = BitcoinScriptList()
        sorted_memory_addresses = sorted(constant_memory_regions.keys())
        for key in sorted_memory_addresses:
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
                to_alt_stack=False,
            )

            for letter in reversed(key):
                script.extend([int(letter, 16), "OP_EQUALVERIFY"])

            self.verify_input_nibble_message_from_public_keys(
                script=script,
                public_keys=trace_value_public_keys,
                n0=value_amount_of_nibbles,
                bits_per_digit_checksum=bits_per_digit_checksum,
                to_alt_stack=False,
            )

            script.append(0)
            for letter in reversed(constant_memory_regions[key]):
                script.extend([1, "OP_ROLL", int(letter, 16), "OP_EQUAL", "OP_ADD"])

            script.append(value_amount_of_nibbles)
            script.append("OP_LESSTHAN")

            script_list.append(script)

        return script_list
