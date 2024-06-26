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

        return signatures_dict
