from blockchain_query_services.services.blockchain_query_services_dependency_injection import (
    transaction_info_service,
)


class TransactionPublishedService:

    def __call__(self, tx_id: str):
        try:
            return transaction_info_service(tx_id=tx_id)
        except Exception as e:
            if str(
                e
            ) == "Transaction not found" or "No such mempool or blockchain transaction" in str(e):
                return False
            raise e
