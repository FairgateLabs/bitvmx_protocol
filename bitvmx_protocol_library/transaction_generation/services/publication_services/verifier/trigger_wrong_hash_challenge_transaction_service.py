from bitcoinutils.constants import TAPROOT_SIGHASH_ALL
from bitcoinutils.keys import PrivateKey
from bitcoinutils.transactions import TxWitnessInput
from bitcoinutils.utils import ControlBlock

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_verifier_dto import (
    BitVMXProtocolVerifierDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_verifier_private_dto import (
    BitVMXProtocolVerifierPrivateDTO,
)
from bitvmx_protocol_library.script_generation.services.bitvmx_bitcoin_scripts_generator_service import (
    BitVMXBitcoinScriptsGeneratorService,
)
from bitvmx_protocol_library.script_generation.services.script_generation.verifier.trigger_wrong_hash_challenge_script_generator_service import (
    TriggerWrongHashChallengeScriptGeneratorService,
)
from bitvmx_protocol_library.winternitz_keys_handling.services.generate_witness_from_input_nibbles_service import (
    GenerateWitnessFromInputNibblesService,
)
from blockchain_query_services.services.blockchain_query_services_dependency_injection import (
    broadcast_transaction_service,
)


class TriggerWrongHashChallengeTransactionService:
    def __init__(self, verifier_private_key):
        self.verifier_wrong_hash_script_generator_service = (
            TriggerWrongHashChallengeScriptGeneratorService()
        )
        self.generate_witness_from_input_nibbles_service = GenerateWitnessFromInputNibblesService(
            verifier_private_key
        )

    def __call__(
        self,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        bitvmx_protocol_verifier_private_dto: BitVMXProtocolVerifierPrivateDTO,
        bitvmx_protocol_verifier_dto: BitVMXProtocolVerifierDTO,
    ):

        bitvmx_bitcoin_scripts_generator_service = BitVMXBitcoinScriptsGeneratorService()
        bitvmx_bitcoin_scripts_dto = bitvmx_bitcoin_scripts_generator_service(
            bitvmx_protocol_setup_properties_dto=bitvmx_protocol_setup_properties_dto,
            signature_public_keys=bitvmx_protocol_setup_properties_dto.signature_public_keys,
        )

        trigger_challenge_taptree = bitvmx_bitcoin_scripts_dto.trigger_challenge_taptree()
        trigger_challenge_scripts_address = bitvmx_bitcoin_scripts_dto.trigger_challenge_address(
            bitvmx_protocol_setup_properties_dto.unspendable_public_key
        )

        wrong_hash_control_block = ControlBlock(
            bitvmx_protocol_setup_properties_dto.unspendable_public_key,
            scripts=trigger_challenge_taptree,
            index=bitvmx_bitcoin_scripts_dto.trigger_wrong_hash_challenge_index(0),
            is_odd=trigger_challenge_scripts_address.is_odd(),
        )

        private_key = PrivateKey(
            b=bytes.fromhex(bitvmx_protocol_verifier_private_dto.verifier_signature_private_key)
        )
        wrong_hash_challenge_signature = private_key.sign_taproot_input(
            bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_wrong_hash_challenge_tx,
            0,
            [trigger_challenge_scripts_address.to_script_pub_key()],
            [
                bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_wrong_hash_challenge_tx.outputs[
                    0
                ].amount
                + bitvmx_protocol_setup_properties_dto.step_fees_satoshis
            ],
            script_path=True,
            tapleaf_script=bitvmx_bitcoin_scripts_dto.wrong_hash_challenge_scripts[0],
            sighash=TAPROOT_SIGHASH_ALL,
            tweak=False,
        )

        trigger_execution_challenge_signature = [wrong_hash_challenge_signature]
        trigger_challenge_witness = []

        bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_wrong_hash_challenge_tx.witnesses.append(
            TxWitnessInput(
                trigger_execution_challenge_signature
                + trigger_challenge_witness
                + [
                    bitvmx_bitcoin_scripts_dto.wrong_hash_challenge_scripts[0].to_hex(),
                    wrong_hash_control_block.to_hex(),
                ]
            )
        )

        broadcast_transaction_service(
            transaction=bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_wrong_hash_challenge_tx.serialize()
        )

        print(
            "Trigger wrong hash challenge transaction: "
            + bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_wrong_hash_challenge_tx.get_txid()
        )
        return (
            bitvmx_protocol_setup_properties_dto.bitvmx_transactions_dto.trigger_wrong_hash_challenge_tx
        )
