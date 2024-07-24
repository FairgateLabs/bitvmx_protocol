from prover_app.config import protocol_properties, Networks
if protocol_properties.network == Networks.MUTINYNET:
    from mutinyet_api.services.transaction_info_service import TransactionInfoService
elif protocol_properties.network == Networks.TESTNET:
    from testnet_api.services.transaction_info_service import TransactionInfoService


class TransactionPublishedService:

    def __init__(self):
        self.transaction_info_service = TransactionInfoService()

    def __call__(self, tx_id: str):
        try:
            return self.transaction_info_service(tx_id=tx_id)
        except Exception as e:
            if str(e) == "Transaction not found":
                return False
            raise e
