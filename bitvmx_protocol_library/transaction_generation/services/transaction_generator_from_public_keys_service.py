from bitcoinutils.keys import P2wpkhAddress
from bitcoinutils.transactions import Transaction, TxInput, TxOutput

from bitvmx_protocol_library.bitvmx_protocol_definition.entities.bitvmx_protocol_setup_properties_dto import (
    BitVMXProtocolSetupPropertiesDTO,
)
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
        bitvmx_protocol_setup_properties_dto: BitVMXProtocolSetupPropertiesDTO,
    ) -> BitVMXTransactionsDTO:

        destroyed_public_key = bitvmx_protocol_setup_properties_dto.unspendable_public_key

        funding_txin = TxInput(
            bitvmx_protocol_setup_properties_dto.funding_tx_id,
            bitvmx_protocol_setup_properties_dto.funding_index,
        )

        hash_result_script_address = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.hash_result_script.get_taproot_address(
            bitvmx_protocol_setup_properties_dto.unspendable_public_key
        )

        funding_txout = TxOutput(
            bitvmx_protocol_setup_properties_dto.funding_amount_of_satoshis,
            hash_result_script_address.to_script_pub_key(),
        )
        funding_tx = Transaction([funding_txin], [funding_txout], has_segwit=True)

        trigger_protocol_script_address = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_protocol_scripts_list.get_taproot_address(
            public_key=destroyed_public_key
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

        hash_search_scripts_addresses = []
        for i in range(
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_wrong_step_search_iterations
        ):
            hash_search_scripts_addresses.append(
                bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.hash_search_scripts_list(
                    iteration=i
                ).get_taproot_address(
                    public_key=destroyed_public_key
                )
            )

        choice_search_scripts_addresses = []
        for i in range(
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_wrong_step_search_iterations
        ):
            choice_search_scripts_addresses.append(
                bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.choice_search_scripts_list(
                    iteration=i
                ).get_taproot_address(
                    public_key=destroyed_public_key
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

        trace_script_address = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trace_script_list.get_taproot_address(
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
            if (
                i
                == bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_wrong_step_search_iterations
                - 1
            ):
                current_output_address = trace_script_address
            else:
                current_output_address = hash_search_scripts_addresses[i + 1]
            current_txout = TxOutput(
                current_output_amount, current_output_address.to_script_pub_key()
            )
            current_tx = Transaction([current_txin], [current_txout], has_segwit=True)
            search_choice_tx_list.append(current_tx)
            previous_tx_id = current_tx.get_txid()

        trigger_challenge_script_address = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_trace_challenge_address(
            destroyed_public_key=destroyed_public_key
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
        execution_challenge_address = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.execution_challenge_script_list.get_taproot_address(
            destroyed_public_key
        )

        trigger_execution_challenge_txin = TxInput(trace_tx.get_txid(), 0)
        trigger_execution_challenge_txout = TxOutput(
            trigger_challenge_output_amount,
            execution_challenge_address.to_script_pub_key(),
        )
        trigger_execution_challenge_tx = Transaction(
            [trigger_execution_challenge_txin], [trigger_execution_challenge_txout], has_segwit=True
        )

        trigger_wrong_pc_txin = TxInput(trace_tx.get_txid(), 0)
        trigger_wrong_pc_output_address = P2wpkhAddress.from_address(
            address=bitvmx_protocol_setup_properties_dto.verifier_destination_address
        )
        trigger_wrong_pc_output_amount = (
            trace_output_amount - bitvmx_protocol_setup_properties_dto.step_fees_satoshis * 4
        )
        trigger_wrong_pc_txout = TxOutput(
            trigger_wrong_pc_output_amount,
            trigger_wrong_pc_output_address.to_script_pub_key(),
        )
        trigger_wrong_pc_tx = Transaction(
            [trigger_wrong_pc_txin], [trigger_wrong_pc_txout], has_segwit=True
        )

        trigger_wrong_hash_txin = TxInput(trace_tx.get_txid(), 0)
        trigger_wrong_hash_output_address = P2wpkhAddress.from_address(
            address=bitvmx_protocol_setup_properties_dto.verifier_destination_address
        )
        trigger_wrong_hash_output_amount = (
            trace_output_amount - bitvmx_protocol_setup_properties_dto.step_fees_satoshis * 4
        )
        trigger_wrong_hash_txout = TxOutput(
            trigger_wrong_hash_output_amount,
            trigger_wrong_hash_output_address.to_script_pub_key(),
        )

        trigger_wrong_hash_tx = Transaction(
            [trigger_wrong_hash_txin], [trigger_wrong_hash_txout], has_segwit=True
        )

        trigger_equivocation_txin = TxInput(trace_tx.get_txid(), 0)
        trigger_equivocation_output_address = P2wpkhAddress.from_address(
            address=bitvmx_protocol_setup_properties_dto.verifier_destination_address
        )
        trigger_equivocation_output_amount = (
            trace_output_amount - bitvmx_protocol_setup_properties_dto.step_fees_satoshis
        )
        trigger_equivocation_txout = TxOutput(
            trigger_equivocation_output_amount,
            trigger_equivocation_output_address.to_script_pub_key(),
        )
        trigger_equivocation_tx = Transaction(
            [trigger_equivocation_txin], [trigger_equivocation_txout], has_segwit=True
        )

        execution_challenge_txin = TxInput(trigger_execution_challenge_tx.get_txid(), 0)

        execution_challenge_output_address = P2wpkhAddress.from_address(
            address=bitvmx_protocol_setup_properties_dto.prover_destination_address
        )

        execution_challenge_txout = TxOutput(
            challenge_output_amount,
            execution_challenge_output_address.to_script_pub_key(),
        )

        execution_challenge_tx = Transaction(
            [execution_challenge_txin], [execution_challenge_txout], has_segwit=True
        )

        hash_read_search_scripts_addresses = []
        for i in range(
            1,
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_wrong_step_search_iterations,
        ):
            hash_read_search_scripts_addresses.append(
                bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.hash_read_search_scripts_address(
                    destroyed_public_key=destroyed_public_key,
                    iteration=i,
                )
            )

        choice_read_search_scripts_addresses = []
        for i in range(
            1,
            bitvmx_protocol_setup_properties_dto.bitvmx_protocol_properties_dto.amount_of_wrong_step_search_iterations,
        ):
            choice_read_search_scripts_addresses.append(
                bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.choice_read_search_scripts_address(
                    destroyed_public_key=destroyed_public_key,
                    iteration=i,
                )
            )

        read_search_hash_tx_list = []
        read_search_choice_tx_list = []
        read_search_equivocation_tx_list = []

        first_choice_txin = TxInput(trace_tx.get_txid(), 0)
        first_choice_output_address = hash_read_search_scripts_addresses[0]
        first_choice_txout = TxOutput(
            trigger_challenge_output_amount,
            first_choice_output_address.to_script_pub_key(),
        )
        read_search_choice_tx_list.append(
            Transaction([first_choice_txin], [first_choice_txout], has_segwit=True)
        )

        previous_tx_id = read_search_choice_tx_list[-1].get_txid()
        current_output_amount = trigger_challenge_output_amount

        read_trace_script_address = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.read_trace_script_list.get_taproot_address(
            destroyed_public_key
        )

        for i in range(len(hash_read_search_scripts_addresses)):
            # HASH
            current_txin = TxInput(previous_tx_id, 0)
            current_output_amount -= bitvmx_protocol_setup_properties_dto.step_fees_satoshis
            # The first one is contained in the trigger challenge taproot -> We could be appending a None, it's never used
            current_output_address = choice_read_search_scripts_addresses[i]
            current_txout = TxOutput(
                current_output_amount, current_output_address.to_script_pub_key()
            )
            current_hash_tx = Transaction([current_txin], [current_txout], has_segwit=True)
            read_search_hash_tx_list.append(current_hash_tx)

            # CHOICE
            current_txin = TxInput(current_hash_tx.get_txid(), 0)
            current_output_amount -= bitvmx_protocol_setup_properties_dto.step_fees_satoshis
            if i == len(hash_read_search_scripts_addresses) - 1:
                current_output_address = read_trace_script_address
            else:
                current_output_address = hash_read_search_scripts_addresses[i + 1]
            current_txout = TxOutput(
                current_output_amount, current_output_address.to_script_pub_key()
            )
            current_choice_tx = Transaction([current_txin], [current_txout], has_segwit=True)
            read_search_choice_tx_list.append(current_choice_tx)
            previous_tx_id = current_choice_tx.get_txid()

            # EQUIVOCATION
            current_txin = TxInput(current_hash_tx.get_txid(), 0)
            current_output_address = P2wpkhAddress.from_address(
                address=bitvmx_protocol_setup_properties_dto.verifier_destination_address
            )
            current_txout = TxOutput(
                current_output_amount, current_output_address.to_script_pub_key()
            )
            current_equivocation_tx = Transaction([current_txin], [current_txout], has_segwit=True)
            read_search_equivocation_tx_list.append(current_equivocation_tx)

        trigger_read_challenge_scripts_address = bitvmx_protocol_setup_properties_dto.bitvmx_bitcoin_scripts_dto.trigger_read_challenge_scripts_list.get_taproot_address(
            public_key=destroyed_public_key
        )

        current_output_amount -= bitvmx_protocol_setup_properties_dto.step_fees_satoshis

        read_trace_txin = TxInput(read_search_choice_tx_list[-1].get_txid(), 0)

        read_trace_txout = TxOutput(
            current_output_amount, trigger_read_challenge_scripts_address.to_script_pub_key()
        )

        read_trace_tx = Transaction([read_trace_txin], [read_trace_txout], has_segwit=True)

        trigger_read_challenge_output_amount = (
            current_output_amount - 4 * bitvmx_protocol_setup_properties_dto.step_fees_satoshis
        )

        trigger_read_challenge_destination_address = P2wpkhAddress.from_address(
            address=bitvmx_protocol_setup_properties_dto.verifier_destination_address
        )
        trigger_read_challenge_txin = TxInput(read_trace_tx.get_txid(), 0)
        trigger_read_challenge_txout = TxOutput(
            trigger_read_challenge_output_amount,
            trigger_read_challenge_destination_address.to_script_pub_key(),
        )
        trigger_read_challenge_tx = Transaction(
            [trigger_read_challenge_txin], [trigger_read_challenge_txout], has_segwit=True
        )

        return BitVMXTransactionsDTO(
            funding_tx=funding_tx,
            hash_result_tx=hash_result_tx,
            trigger_protocol_tx=trigger_protocol_tx,
            search_hash_tx_list=search_hash_tx_list,
            search_choice_tx_list=search_choice_tx_list,
            trace_tx=trace_tx,
            trigger_execution_challenge_tx=trigger_execution_challenge_tx,
            trigger_equivocation_tx=trigger_equivocation_tx,
            trigger_wrong_hash_challenge_tx=trigger_wrong_hash_tx,
            trigger_wrong_program_counter_challenge_tx=trigger_wrong_pc_tx,
            execution_challenge_tx=execution_challenge_tx,
            read_search_hash_tx_list=read_search_hash_tx_list,
            read_search_choice_tx_list=read_search_choice_tx_list,
            read_trace_tx=read_trace_tx,
            trigger_read_challenge_tx=trigger_read_challenge_tx,
            read_search_equivocation_tx_list=read_search_equivocation_tx_list,
        )
