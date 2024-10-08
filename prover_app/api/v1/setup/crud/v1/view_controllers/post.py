import secrets

from bitcoinutils.keys import PrivateKey

from prover_app.api.v1.setup.crud.v1.view_models.post import SetupPostV1Input, SetupPostV1Output


class SetupPostViewControllerV1:
    def __init__(
        self,
        create_setup_controller,
        protocol_properties,
        common_protocol_properties,
    ):
        self.create_setup_controller = create_setup_controller
        self.protocol_properties = protocol_properties
        self.common_protocol_properties = common_protocol_properties

    async def __call__(self, setup_post_view_input: SetupPostV1Input) -> SetupPostV1Output:
        if setup_post_view_input.verifier_list is None:
            verifier_list = self.protocol_properties.verifier_list
        else:
            verifier_list = setup_post_view_input.verifier_list
        if self.protocol_properties.prover_private_key is None:
            controlled_prover_private_key = PrivateKey(b=secrets.token_bytes(32))
        else:
            controlled_prover_private_key = PrivateKey(
                b=bytes.fromhex(self.protocol_properties.prover_private_key)
            )

        origin_of_funds_private_key = PrivateKey(
            b=bytes.fromhex(setup_post_view_input.secret_origin_of_funds)
        )

        setup_uuid = await self.create_setup_controller(
            max_amount_of_steps=setup_post_view_input.max_amount_of_steps,
            amount_of_input_words=setup_post_view_input.amount_of_input_words,
            amount_of_bits_wrong_step_search=setup_post_view_input.amount_of_bits_wrong_step_search,
            amount_of_bits_per_digit_checksum=setup_post_view_input.amount_of_bits_per_digit_checksum,
            verifier_list=verifier_list,
            controlled_prover_private_key=controlled_prover_private_key,
            funding_tx_id=setup_post_view_input.funding_tx_id,
            funding_index=setup_post_view_input.funding_index,
            step_fees_satoshis=self.common_protocol_properties.step_fees_satoshis,
            origin_of_funds_private_key=origin_of_funds_private_key,
            prover_destination_address=setup_post_view_input.prover_destination_address,
            prover_signature_private_key=setup_post_view_input.prover_signature_private_key,
            prover_signature_public_key=setup_post_view_input.prover_signature_public_key,
        )
        return SetupPostV1Output(setup_uuid=setup_uuid)
