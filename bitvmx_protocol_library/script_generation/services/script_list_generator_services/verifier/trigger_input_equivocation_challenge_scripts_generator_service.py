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


class TriggerInputEquivocationChallengeScriptsGeneratorService:
    def __init__(self):
        pass

    def __call__(
        self,
        signature_public_keys: List[str],
        base_input_address: str,
        amount_of_input_words: int,
        address_public_keys: List[str],
        address_amount_of_nibbles: int,
        value_public_keys: List[str],
        value_amount_of_nibbles: int,
    ) -> BitcoinScriptList:

        script_list = BitcoinScriptList()

        input_and_constant_addresses_generation_service = (
            InputAndConstantAddressesGenerationService(
                instruction_commitment=ExecutionTraceGenerationService.commitment_file()
            )
        )
        static_addresses = input_and_constant_addresses_generation_service(
            input_length=amount_of_input_words
        )

        for i in range(amount_of_input_words):

            script = BitcoinScript()

            for signature_public_key in reversed(signature_public_keys):
                script.extend(
                    [PublicKey(hex_str=signature_public_key).to_x_only_hex(), "OP_CHECKSIGVERIFY"]
                )

            script.append(1)

            script_list.append(script)

        return script_list
