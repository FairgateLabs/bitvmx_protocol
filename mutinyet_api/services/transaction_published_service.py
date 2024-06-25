from mutinyet_api.services.transaction_info_service import TransactionInfoService


class TransactionPublishedService:

    def __init__(self):
        self.transaction_info_service = TransactionInfoService()

    def __call__(self, tx_id: str):
        try:
            self.transaction_info_service(tx_id=tx_id)
            return True
        except Exception as e:
            if str(e) == "Transaction not found":
                return False
            raise e