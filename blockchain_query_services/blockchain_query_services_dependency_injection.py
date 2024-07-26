from dependency_injector import containers, providers

from blockchain_query_services.mainnet_api.services.broadcast_transaction_service import (
    BroadcastTransactionService as BroadcastTransactionServiceMainnet,
)
from blockchain_query_services.mutinyet_api.services.broadcast_transaction_service import (
    BroadcastTransactionService as BroadcastTransactionServiceMutinynet,
)
from blockchain_query_services.testnet_api.services.broadcast_transaction_service import (
    BroadcastTransactionService as BroadcastTransactionServiceTestnet,
)


class BroadcastTransactionServices(containers.DeclarativeContainer):

    mutinynet = providers.Singleton(BroadcastTransactionServiceMutinynet)
    testnet = providers.Singleton(BroadcastTransactionServiceTestnet)
    mainnet = providers.Singleton(BroadcastTransactionServiceMainnet)


broadcast_transaction_service = BroadcastTransactionServices.mutinynet
