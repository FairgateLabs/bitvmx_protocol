from bitcoinutils.keys import P2wpkhAddress, PublicKey
from bitcoinutils.transactions import Transaction, TxInput, TxOutput

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_properties_dto import (
    BitVMXProtocolPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_prover_winternitz_public_keys_dto import (
    BitVMXProverWinternitzPublicKeysDTO,
)
from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_verifier_winternitz_public_keys_dto import (
    BitVMXVerifierWinternitzPublicKeysDTO,
)
from bitvmx_protocol_library.config import common_protocol_properties
from bitvmx_protocol_library.enums import BitcoinNetwork
from bitvmx_protocol_library.script_generation.services.bitvmx_bitcoin_scripts_generator_service import (
    BitVMXBitcoinScriptsGeneratorService,
)
from bitvmx_protocol_library.transaction_generation.entities.dtos.bitvmx_transactions_dto import (
    BitVMXTransactionsDTO,
)


class TransactionGeneratorFromPublicKeysService:

    def __init__(self):
        self.bitvmx_bitcoin_scripts_generator_service = BitVMXBitcoinScriptsGeneratorService()

    def __call__(
        self,
        protocol_dict,
        bitvmx_protocol_properties_dto: BitVMXProtocolPropertiesDTO,
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
        bitvmx_prover_winternitz_public_keys_dto: BitVMXProverWinternitzPublicKeysDTO,
        bitvmx_verifier_winternitz_public_keys_dto: BitVMXVerifierWinternitzPublicKeysDTO,
    ) -> BitVMXTransactionsDTO:

        destroyed_public_key = PublicKey(hex_str="02" + protocol_dict["destroyed_public_key"])

        bitvmx_bitcoin_scripts_dto = self.bitvmx_bitcoin_scripts_generator_service(
            bitvmx_protocol_properties_dto=bitvmx_protocol_properties_dto,
            bitvmx_prover_winternitz_public_keys_dto=bitvmx_prover_winternitz_public_keys_dto,
            bitvmx_verifier_winternitz_public_keys_dto=bitvmx_verifier_winternitz_public_keys_dto,
            signature_public_keys=protocol_dict["public_keys"],
        )

        funding_txin = TxInput(
            bitvmx_protocol_setup_properties_dto.funding_tx_id,
            bitvmx_protocol_setup_properties_dto.funding_index,
        )

        hash_result_script_address = (
            bitvmx_bitcoin_scripts_dto.hash_result_script.get_taproot_address(destroyed_public_key)
        )

        funding_txout = TxOutput(
            bitvmx_protocol_setup_properties_dto.funding_amount_of_satoshis,
            hash_result_script_address.to_script_pub_key(),
        )
        funding_tx = Transaction([funding_txin], [funding_txout], has_segwit=True)

        trigger_protocol_script_address = (
            bitvmx_bitcoin_scripts_dto.trigger_protocol_script.get_taproot_address(
                destroyed_public_key
            )
        )

        hash_result_txin = TxInput(funding_tx.get_txid(), 0)
        hash_result_output_amount = (
            bitvmx_protocol_setup_properties_dto.funding_amount_of_satoshis
            - bitvmx_protocol_setup_properties_dto.step_fees_satoshis
        )
        # first_txOut = TxOutput(first_output_amount, P2wpkhAddress.from_address(address=faucet_address).to_script_pub_key())
        hash_result_txOut = TxOutput(
            hash_result_output_amount, trigger_protocol_script_address.to_script_pub_key()
        )

        hash_result_tx = Transaction([hash_result_txin], [hash_result_txOut], has_segwit=True)

        hash_search_scripts_addresses = list(
            map(
                lambda search_script: search_script.get_taproot_address(destroyed_public_key),
                bitvmx_bitcoin_scripts_dto.hash_search_scripts,
            )
        )

        choice_search_scripts_addresses = list(
            map(
                lambda choice_script: choice_script.get_taproot_address(destroyed_public_key),
                bitvmx_bitcoin_scripts_dto.choice_search_scripts,
            )
        )

        trigger_protocol_output_amount = (
            hash_result_output_amount - bitvmx_protocol_setup_properties_dto.step_fees_satoshis
        )
        trigger_protocol_txin = TxInput(hash_result_tx.get_txid(), 0)
        trigger_protocol_txOut = TxOutput(
            trigger_protocol_output_amount, hash_search_scripts_addresses[0].to_script_pub_key()
        )

        trigger_protocol_tx = Transaction(
            [trigger_protocol_txin], [trigger_protocol_txOut], has_segwit=True
        )

        previous_tx_id = trigger_protocol_tx.get_txid()
        current_output_amount = trigger_protocol_output_amount
        search_hash_tx_list = []
        search_choice_tx_list = []

        trace_script_address = bitvmx_bitcoin_scripts_dto.trace_script.get_taproot_address(
            destroyed_public_key
        )

        for i in range(len(choice_search_scripts_addresses)):

            # HASH
            current_txin = TxInput(previous_tx_id, 0)
            current_output_amount -= bitvmx_protocol_setup_properties_dto.step_fees_satoshis
            current_output_address = choice_search_scripts_addresses[i]
            current_txout = TxOutput(
                current_output_amount, current_output_address.to_script_pub_key()
            )
            current_tx = Transaction([current_txin], [current_txout], has_segwit=True)
            search_hash_tx_list.append(current_tx)

            # CHOICE
            current_txin = TxInput(current_tx.get_txid(), 0)
            current_output_amount -= bitvmx_protocol_setup_properties_dto.step_fees_satoshis
            if i == bitvmx_protocol_properties_dto.amount_of_wrong_step_search_iterations - 1:
                current_output_address = trace_script_address
            else:
                current_output_address = hash_search_scripts_addresses[i + 1]
            current_txout = TxOutput(
                current_output_amount, current_output_address.to_script_pub_key()
            )
            current_tx = Transaction([current_txin], [current_txout], has_segwit=True)
            search_choice_tx_list.append(current_tx)
            previous_tx_id = current_tx.get_txid()

        trigger_challenge_script_address = (
            bitvmx_bitcoin_scripts_dto.trigger_challenge_scripts.get_taproot_address(
                destroyed_public_key
            )
        )

        trace_txin = TxInput(search_choice_tx_list[-1].get_txid(), 0)
        trace_output_amount = (
            current_output_amount - bitvmx_protocol_setup_properties_dto.step_fees_satoshis
        )
        trace_txout = TxOutput(
            trace_output_amount, trigger_challenge_script_address.to_script_pub_key()
        )

        trace_tx = Transaction([trace_txin], [trace_txout], has_segwit=True)

        trigger_challenge_output_amount = (
            trace_output_amount - bitvmx_protocol_setup_properties_dto.step_fees_satoshis
        )
        challenge_output_amount = (
            trigger_challenge_output_amount
            - bitvmx_protocol_setup_properties_dto.step_fees_satoshis
        )

        #  Here we should put all the challenges

        # TODO: cache in class
        ## Execution challenge
        if "execution_challenge_address" in protocol_dict:
            execution_challenge_address = protocol_dict["execution_challenge_address"]
        else:
            execution_challenge_address = (
                bitvmx_bitcoin_scripts_dto.execution_challenge_script_list.get_taproot_address(
                    destroyed_public_key
                )
            )

            protocol_dict["execution_challenge_address"] = execution_challenge_address

        trigger_execution_challenge_txin = TxInput(trace_tx.get_txid(), 0)
        trigger_execution_challenge_txout = TxOutput(
            trigger_challenge_output_amount,
            execution_challenge_address.to_script_pub_key(),
        )
        trigger_execution_challenge_tx = Transaction(
            [trigger_execution_challenge_txin], [trigger_execution_challenge_txout], has_segwit=True
        )

        execution_challenge_txin = TxInput(trigger_execution_challenge_tx.get_txid(), 0)

        if common_protocol_properties.network == BitcoinNetwork.MUTINYNET:
            faucet_address = "tb1qd28npep0s8frcm3y7dxqajkcy2m40eysplyr9v"
            execution_challenge_output_address = P2wpkhAddress.from_address(address=faucet_address)
        else:
            execution_challenge_output_address = P2wpkhAddress.from_address(
                address=protocol_dict["controlled_prover_address"]
            )

        execution_challenge_txout = TxOutput(
            challenge_output_amount,
            execution_challenge_output_address.to_script_pub_key(),
        )

        execution_challenge_tx = Transaction(
            [execution_challenge_txin], [execution_challenge_txout], has_segwit=True
        )

        protocol_dict["last_confirmed_step"] = None
        protocol_dict["last_confirmed_step_tx_id"] = None

        return BitVMXTransactionsDTO(
            funding_tx=funding_tx,
            hash_result_tx=hash_result_tx,
            trigger_protocol_tx=trigger_protocol_tx,
            search_hash_tx_list=search_hash_tx_list,
            search_choice_tx_list=search_choice_tx_list,
            trace_tx=trace_tx,
            trigger_execution_challenge_tx=trigger_execution_challenge_tx,
            execution_challenge_tx=execution_challenge_tx,
        )
