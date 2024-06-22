from bitcoinutils.keys import P2wpkhAddress, PublicKey
from bitcoinutils.transactions import Transaction, TxInput, TxOutput

from scripts.scripts_dict_generator_service import ScriptsDictGeneratorService


class TransactionGeneratorFromPublicKeysService:

    def __init__(self):
        self.scripts_dict_generator_service = ScriptsDictGeneratorService()

    def __call__(self, protocol_dict):

        faucet_tx_id = protocol_dict["faucet_tx_id"]
        faucet_index = protocol_dict["faucet_index"]
        funding_result_output_amount = protocol_dict["funding_amount_satoshis"]
        step_fees_satoshis = protocol_dict["step_fees_satoshis"]
        amount_of_wrong_step_search_iterations = protocol_dict[
            "amount_of_wrong_step_search_iterations"
        ]

        destroyed_public_key = PublicKey(hex_str=protocol_dict["destroyed_public_key"])

        scripts_dict = self.scripts_dict_generator_service(protocol_dict)

        funding_txin = TxInput(faucet_tx_id, faucet_index)
        # hash_result_script_address = destroyed_public_key.get_taproot_address([[hash_result_script]])

        protocol_dict["funding_amount_satoshis"] = funding_result_output_amount

        hash_result_script_address = destroyed_public_key.get_taproot_address(
            [[scripts_dict["hash_result_script"]]]
        )

        funding_txout = TxOutput(
            funding_result_output_amount, hash_result_script_address.to_script_pub_key()
        )
        funding_tx = Transaction([funding_txin], [funding_txout], has_segwit=True)

        protocol_dict["funding_tx"] = funding_tx

        trigger_protocol_script_address = destroyed_public_key.get_taproot_address(
            [[scripts_dict["trigger_protocol_script"]]]
        )

        hash_result_txin = TxInput(funding_tx.get_txid(), 0)
        hash_result_output_amount = funding_result_output_amount - step_fees_satoshis
        # first_txOut = TxOutput(first_output_amount, P2wpkhAddress.from_address(address=faucet_address).to_script_pub_key())
        hash_result_txOut = TxOutput(
            hash_result_output_amount, trigger_protocol_script_address.to_script_pub_key()
        )

        hash_result_tx = Transaction([hash_result_txin], [hash_result_txOut], has_segwit=True)

        protocol_dict["hash_result_tx"] = hash_result_tx

        hash_search_scripts = scripts_dict["hash_search_scripts"]
        choice_search_scripts = scripts_dict["choice_search_scripts"]

        hash_search_scripts_addresses = list(
            map(
                lambda search_script: destroyed_public_key.get_taproot_address([[search_script]]),
                hash_search_scripts,
            )
        )

        choice_search_scripts_addresses = list(
            map(
                lambda choice_script: destroyed_public_key.get_taproot_address([[choice_script]]),
                choice_search_scripts,
            )
        )

        trigger_protocol_output_amount = hash_result_output_amount - step_fees_satoshis
        trigger_protocol_txin = TxInput(hash_result_tx.get_txid(), 0)
        trigger_protocol_txOut = TxOutput(
            trigger_protocol_output_amount, hash_search_scripts_addresses[0].to_script_pub_key()
        )

        trigger_protocol_tx = Transaction(
            [trigger_protocol_txin], [trigger_protocol_txOut], has_segwit=True
        )

        protocol_dict["trigger_protocol_tx"] = trigger_protocol_tx

        previous_tx_id = trigger_protocol_tx.get_txid()
        current_output_amount = trigger_protocol_output_amount
        search_hash_tx_list = []
        choice_hash_tx_list = []

        trace_script_address = destroyed_public_key.get_taproot_address(
            [[scripts_dict["trace_script"]]]
        )

        for i in range(len(choice_search_scripts_addresses)):

            # HASH
            current_txin = TxInput(previous_tx_id, 0)
            current_output_amount -= step_fees_satoshis
            current_output_address = choice_search_scripts_addresses[i]
            current_txout = TxOutput(
                current_output_amount, current_output_address.to_script_pub_key()
            )
            current_tx = Transaction([current_txin], [current_txout], has_segwit=True)
            search_hash_tx_list.append(current_tx)

            # CHOICE
            current_txin = TxInput(current_tx.get_txid(), 0)
            current_output_amount -= step_fees_satoshis
            if i == amount_of_wrong_step_search_iterations - 1:
                current_output_address = trace_script_address
            else:
                current_output_address = hash_search_scripts_addresses[i + 1]
            current_txout = TxOutput(
                current_output_amount, current_output_address.to_script_pub_key()
            )
            current_tx = Transaction([current_txin], [current_txout], has_segwit=True)
            choice_hash_tx_list.append(current_tx)
            previous_tx_id = current_tx.get_txid()

        protocol_dict["search_hash_tx_list"] = search_hash_tx_list
        protocol_dict["choice_hash_tx_list"] = choice_hash_tx_list

        trace_txin = TxInput(choice_hash_tx_list[-1].get_txid(), 0)
        trace_output_amount = current_output_amount - step_fees_satoshis
        faucet_address = "tb1qd28npep0s8frcm3y7dxqajkcy2m40eysplyr9v"
        trace_output_address = P2wpkhAddress.from_address(address=faucet_address)
        trace_txout = TxOutput(trace_output_amount, trace_output_address.to_script_pub_key())

        trace_tx = Transaction([trace_txin], [trace_txout], has_segwit=True)
        protocol_dict["trace_tx"] = trace_tx

        protocol_dict["transactions"] = protocol_dict

        protocol_dict["last_confirmed_step"] = None
        protocol_dict["last_confirmed_step_tx_id"] = None
