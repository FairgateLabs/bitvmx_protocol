from bitcoinutils.constants import TAPROOT_SIGHASH_ALL
from bitcoinutils.keys import PublicKey
from bitcoinutils.schnorr import schnorr_verify


class VerifySignatureService:

    def __init__(self, unspendable_public_key: PublicKey):
        self.unspendable_public_key = unspendable_public_key

    def __call__(self, tx, script, script_address, amount, public_key_hex, signature):

        # script_address = self.unspendable_public_key.get_taproot_address([[script]])
        tx_digest = tx.get_transaction_taproot_digest(
            0,
            [script_address.to_script_pub_key()],
            [amount],
            1,
            script=script,
            sighash=TAPROOT_SIGHASH_ALL,
        )
        assert schnorr_verify(
            tx_digest,
            bytes.fromhex(PublicKey(public_key_hex).to_x_only_hex()),
            bytes.fromhex(signature),
        )
