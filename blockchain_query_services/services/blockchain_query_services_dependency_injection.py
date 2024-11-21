from dependency_injector import containers, providers

from bitvmx_protocol_library.config import common_protocol_properties
from bitvmx_protocol_library.enums import BitcoinNetwork
from blockchain_query_services.services.mainnet_api.broadcast_transaction_service import (
    BroadcastTransactionService as BroadcastTransactionServiceMainnet,
)
from blockchain_query_services.services.mainnet_api.transaction_info_service import (
    TransactionInfoService as TransactionInfoServiceMainnet,
)
from blockchain_query_services.services.mutinynet_api.broadcast_transaction_service import (
    BroadcastTransactionService as BroadcastTransactionServiceMutinynet,
)
from blockchain_query_services.services.mutinynet_api.faucet_service import (
    FaucetService as FaucetServiceMutinynet,
)
from blockchain_query_services.services.mutinynet_api.transaction_info_service import (
    TransactionInfoService as TransactionInfoServiceMutinynet,
)
from blockchain_query_services.services.regtest_api.broadcast_transaction_service import (
    BroadcastTransactionService as BroadcastTransactionServiceRegtest,
)
from blockchain_query_services.services.regtest_api.faucet_service import (
    FaucetService as FaucetServiceRegtest,
)
from blockchain_query_services.services.regtest_api.transaction_info_service import (
    TransactionInfoService as TransactionInfoServiceRegtest,
)
from blockchain_query_services.services.testnet_api.broadcast_transaction_service import (
    BroadcastTransactionService as BroadcastTransactionServiceTestnet,
)
from blockchain_query_services.services.testnet_api.transaction_info_service import (
    TransactionInfoService as TransactionInfoServiceTestnet,
)


class BroadcastTransactionServices(containers.DeclarativeContainer):

    mutinynet = providers.Singleton(BroadcastTransactionServiceMutinynet)
    testnet = providers.Singleton(BroadcastTransactionServiceTestnet)
    mainnet = providers.Singleton(BroadcastTransactionServiceMainnet)
    regtest = providers.Singleton(BroadcastTransactionServiceRegtest)


class TransactionInfoServices(containers.DeclarativeContainer):
    mutinynet = providers.Singleton(TransactionInfoServiceMutinynet)
    testnet = providers.Singleton(TransactionInfoServiceTestnet)
    mainnet = providers.Singleton(TransactionInfoServiceMainnet)
    regtest = providers.Singleton(TransactionInfoServiceRegtest)


class FaucetServices(containers.DeclarativeContainer):
    mutinynet = providers.Singleton(FaucetServiceMutinynet)
    regtest = providers.Singleton(FaucetServiceRegtest)


if common_protocol_properties.network == BitcoinNetwork.MUTINYNET:
    broadcast_transaction_service = BroadcastTransactionServices.mutinynet()
    transaction_info_service = TransactionInfoServices.mutinynet()
    faucet_service = FaucetServices.mutinynet()
elif common_protocol_properties.network == BitcoinNetwork.TESTNET:
    broadcast_transaction_service = BroadcastTransactionServices.testnet()
    transaction_info_service = TransactionInfoServices.testnet()
elif common_protocol_properties.network == BitcoinNetwork.MAINNET:
    broadcast_transaction_service = BroadcastTransactionServices.mainnet()
    transaction_info_service = TransactionInfoServices.mainnet()
elif common_protocol_properties.network == BitcoinNetwork.REGTEST:
    broadcast_transaction_service = BroadcastTransactionServices.regtest()
    transaction_info_service = TransactionInfoServices.regtest()
    faucet_service = FaucetServices.regtest()
