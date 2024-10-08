setup_post_v1_input_swagger_examples = {
    "plainc": {
        "summary": "plainc",
        "description": "Working configuration for the sample code in the BitVMX repository",
        "value": {
            "max_amount_of_steps": 1000,
            "amount_of_bits_wrong_step_search": 2,
            "funding_tx_id": "7eaa1105206b94afb9c6bc918f19377a6caa63d6193b668540d997dd4778e195",
            "funding_index": 0,
            "secret_origin_of_funds": "7920e3e47f7c977dab446d6d55ee679241b13c28edf363d519866ede017ef1b4",
            "prover_destination_address": "tb1qd28npep0s8frcm3y7dxqajkcy2m40eysplyr9v",
            "prover_signature_private_key": "f4d3da63c4c8156dc626f97b3cbf970c32b3f20970c41db36c0d7617e460cf89",
            "prover_signature_public_key": "0362d1d2725afa28e9d90ac41b59639b746e72c9d0307f9f21075e7810721f795f",
            "amount_of_input_words": 2,
        },
    },
    "zk_verifier": {
        "summary": "SNARK verifier",
        "description": "Working configuration for the SNARK verification",
        "value": {
            "max_amount_of_steps": 5000000000,
            "amount_of_bits_wrong_step_search": 3,
            "funding_tx_id": "7eaa1105206b94afb9c6bc918f19377a6caa63d6193b668540d997dd4778e195",
            "funding_index": 0,
            "secret_origin_of_funds": "7920e3e47f7c977dab446d6d55ee679241b13c28edf363d519866ede017ef1b4",
            "prover_destination_address": "tb1qd28npep0s8frcm3y7dxqajkcy2m40eysplyr9v",
            "amount_of_input_words": 2,
        },
    },
}
