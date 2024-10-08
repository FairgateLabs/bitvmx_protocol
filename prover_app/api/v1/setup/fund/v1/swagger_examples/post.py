setup_fund_post_v1_input_swagger_examples = {
    "plainc": {
        "summary": "plainc",
        "description": "Working configuration for the sample code in the BitVMX repository",
        "value": {
            "max_amount_of_steps": 1000,
            "amount_of_bits_wrong_step_search": 2,
            "secret_origin_of_funds": "7920e3e47f7c977dab446d6d55ee679241b13c28edf363d519866ede017ef1b4",
            "amount_of_input_words": 2,
        },
    },
    "zk_verifier": {
        "summary": "SNARK verifier",
        "description": "Working configuration for the SNARK verification",
        "value": {
            "max_amount_of_steps": 5000000000,
            "amount_of_bits_wrong_step_search": 3,
            "secret_origin_of_funds": "7920e3e47f7c977dab446d6d55ee679241b13c28edf363d519866ede017ef1b4",
            "amount_of_input_words": 2,
        },
    },
}
