from bitcoinutils.constants import TAPROOT_SIGHASH_ALL


class GenerateSignaturesService:

    def __init__(self, private_key, destroyed_public_key):
        self.private_key = private_key
        self.destroyed_public_key = destroyed_public_key

    def __call__(self, protocol_dict, scripts_dict):
        signatures_dict = {}

        funding_result_output_amount = protocol_dict["funding_amount_satoshis"]
        step_fees_satoshis = protocol_dict["step_fees_satoshis"]

        hash_result_tx = protocol_dict["hash_result_tx"]
        hash_result_script_address = self.destroyed_public_key.get_taproot_address(
            [[scripts_dict["hash_result_script"]]]
        )
        hash_result_signature = self.private_key.sign_taproot_input(
            hash_result_tx,
            0,
            [hash_result_script_address.to_script_pub_key()],
            [funding_result_output_amount],
            script_path=True,
            tapleaf_script=scripts_dict["hash_result_script"],
            sighash=TAPROOT_SIGHASH_ALL,
            tweak=False,
        )
        signatures_dict["hash_result_signature"] = hash_result_signature

        trigger_protocol_tx = protocol_dict["trigger_protocol_tx"]
        trigger_protocol_script_address = self.destroyed_public_key.get_taproot_address(
            [[scripts_dict["trigger_protocol_script"]]]
        )
        trigger_protocol_signature = self.private_key.sign_taproot_input(
            trigger_protocol_tx,
            0,
            [trigger_protocol_script_address.to_script_pub_key()],
            [funding_result_output_amount - step_fees_satoshis],
            script_path=True,
            tapleaf_script=scripts_dict["trigger_protocol_script"],
            sighash=TAPROOT_SIGHASH_ALL,
            tweak=False,
        )
        signatures_dict["trigger_protocol_signature"] = trigger_protocol_signature

        search_hash_signatures = []
        search_choice_signatures = []
        for i in range(len(protocol_dict["search_hash_tx_list"])):
            current_search_hash_tx = protocol_dict["search_hash_tx_list"][i]
            current_search_hash_script_address = self.destroyed_public_key.get_taproot_address(
                [[scripts_dict["hash_search_scripts"][i]]]
            )
            current_search_hash_signature = self.private_key.sign_taproot_input(
                current_search_hash_tx,
                0,
                [current_search_hash_script_address.to_script_pub_key()],
                [funding_result_output_amount - (2 * i + 2) * step_fees_satoshis],
                script_path=True,
                tapleaf_script=scripts_dict["hash_search_scripts"][i],
                sighash=TAPROOT_SIGHASH_ALL,
                tweak=False,
            )
            search_hash_signatures.append(current_search_hash_signature)

            current_search_choice_tx = protocol_dict["search_choice_tx_list"][i]
            current_search_choice_script_address = self.destroyed_public_key.get_taproot_address(
                [[scripts_dict["choice_search_scripts"][i]]]
            )
            current_search_choice_signature = self.private_key.sign_taproot_input(
                current_search_choice_tx,
                0,
                [current_search_choice_script_address.to_script_pub_key()],
                [funding_result_output_amount - (2 * i + 3) * step_fees_satoshis],
                script_path=True,
                tapleaf_script=scripts_dict["choice_search_scripts"][i],
                sighash=TAPROOT_SIGHASH_ALL,
                tweak=False,
            )
            search_choice_signatures.append(current_search_choice_signature)

        signatures_dict["search_hash_signatures"] = search_hash_signatures
        signatures_dict["search_choice_signatures"] = search_choice_signatures

        return signatures_dict
