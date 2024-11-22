from typing import Dict, List, Union

from bitcoinutils.transactions import Transaction
from pydantic import BaseModel, ConfigDict, field_serializer


class BitVMXTransactionsDTO(BaseModel):
    # IMPORTANT #
    # ONLY TRANSACTION AND LIST[TRANSACTION] ALLOWED IN THIS CLASS #
    # If this want to be extended, the serializers and init has to be changed accordingly
    funding_tx: Transaction
    hash_result_tx: Transaction
    trigger_protocol_tx: Transaction
    search_hash_tx_list: List[Transaction]
    search_choice_tx_list: List[Transaction]
    trace_tx: Transaction
    trigger_execution_challenge_tx: Transaction
    trigger_equivocation_tx: Transaction
    trigger_wrong_hash_challenge_tx: Transaction
    trigger_wrong_program_counter_challenge_tx: Transaction
    execution_challenge_tx: Transaction
    read_search_hash_tx_list: List[Transaction]
    read_search_equivocation_tx_list: List[Transaction]
    read_search_choice_tx_list: List[Transaction]
    read_trace_tx: Transaction
    trigger_read_challenge_tx: Transaction

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @staticmethod
    def transform_list_transaction_input(
        input_list: Union[List[Transaction], List[Dict]]
    ) -> List[Transaction]:
        return list(
            map(
                lambda transaction: BitVMXTransactionsDTO.transform_transaction_input(transaction),
                input_list,
            )
        )

    @staticmethod
    def transform_transaction_input(input: Union[Transaction, str]) -> Transaction:
        if isinstance(input, Transaction):
            return input
        return Transaction.from_raw(rawtxhex=input)

    def __init__(self, **data):
        for field_name, field_type in self.__annotations__.items():
            if field_type == Transaction:
                data[field_name] = BitVMXTransactionsDTO.transform_transaction_input(
                    data[field_name]
                )
            elif field_type == List[Transaction]:
                data[field_name] = BitVMXTransactionsDTO.transform_list_transaction_input(
                    data[field_name]
                )
            else:
                raise TypeError(f"Unexpected type {field_type} for field {field_name}")
        super().__init__(**data)

    @staticmethod
    def transaction_to_str(transaction: Transaction) -> str:
        return transaction.to_hex()

    @field_serializer("funding_tx", when_used="always")
    def serialize_funding_tx(funding_tx: Transaction) -> str:
        return BitVMXTransactionsDTO.transaction_to_str(funding_tx)

    @field_serializer("hash_result_tx", when_used="always")
    def serialize_hash_result_tx(hash_result_tx: Transaction) -> str:
        return BitVMXTransactionsDTO.transaction_to_str(hash_result_tx)

    @field_serializer("trigger_protocol_tx", when_used="always")
    def serialize_trigger_protocol_tx(trigger_protocol_tx: Transaction) -> str:
        return BitVMXTransactionsDTO.transaction_to_str(trigger_protocol_tx)

    @field_serializer("search_hash_tx_list", when_used="always")
    def serialize_search_hash_tx_list(search_hash_tx_list: List[Transaction]) -> List[str]:
        return list(
            map(
                lambda transaction: BitVMXTransactionsDTO.transaction_to_str(transaction),
                search_hash_tx_list,
            )
        )

    @field_serializer("search_choice_tx_list", when_used="always")
    def serialize_search_choice_tx_list(search_choice_tx_list: List[Transaction]) -> List[str]:
        return list(
            map(
                lambda transaction: BitVMXTransactionsDTO.transaction_to_str(transaction),
                search_choice_tx_list,
            )
        )

    @field_serializer("trace_tx", when_used="always")
    def serialize_trace_tx(trace_tx: Transaction) -> str:
        return BitVMXTransactionsDTO.transaction_to_str(trace_tx)

    @field_serializer("trigger_execution_challenge_tx", when_used="always")
    def serialize_trigger_execution_challenge_tx(
        trigger_execution_challenge_tx: Transaction,
    ) -> str:
        return BitVMXTransactionsDTO.transaction_to_str(trigger_execution_challenge_tx)

    @field_serializer("trigger_equivocation_tx", when_used="always")
    def serialize_trigger_equivocation_tx(
        trigger_equivocation_tx: Transaction,
    ) -> str:
        return BitVMXTransactionsDTO.transaction_to_str(trigger_equivocation_tx)

    @field_serializer("trigger_wrong_hash_challenge_tx", when_used="always")
    def serialize_trigger_wrong_hash_challenge_tx(
        trigger_wrong_hash_challenge_tx: Transaction,
    ) -> str:
        return BitVMXTransactionsDTO.transaction_to_str(trigger_wrong_hash_challenge_tx)

    @field_serializer("trigger_wrong_program_counter_challenge_tx", when_used="always")
    def serialize_trigger_wrong_program_counter_challenge_tx(
        trigger_wrong_program_counter_challenge_tx: Transaction,
    ) -> str:
        return BitVMXTransactionsDTO.transaction_to_str(trigger_wrong_program_counter_challenge_tx)

    @field_serializer("execution_challenge_tx", when_used="always")
    def serialize_execution_challenge_tx(execution_challenge_tx: Transaction) -> str:
        return BitVMXTransactionsDTO.transaction_to_str(execution_challenge_tx)

    @field_serializer("read_search_hash_tx_list", when_used="always")
    def serialize_read_search_hash_tx_list(
        read_search_hash_tx_list: List[Transaction],
    ) -> List[str]:
        return list(
            map(
                lambda transaction: BitVMXTransactionsDTO.transaction_to_str(transaction),
                read_search_hash_tx_list,
            )
        )

    @field_serializer("read_search_equivocation_tx_list", when_used="always")
    def serialize_read_search_equivocation_tx_list(
        read_search_equivocation_tx_list: List[Transaction],
    ) -> List[str]:
        return list(
            map(
                lambda transaction: BitVMXTransactionsDTO.transaction_to_str(transaction),
                read_search_equivocation_tx_list,
            )
        )

    @field_serializer("read_search_choice_tx_list", when_used="always")
    def serialize_read_search_choice_tx_list(
        read_search_choice_tx_list: List[Transaction],
    ) -> List[str]:
        return list(
            map(
                lambda transaction: BitVMXTransactionsDTO.transaction_to_str(transaction),
                read_search_choice_tx_list,
            )
        )

    @field_serializer("read_trace_tx", when_used="always")
    def serialize_read_trace_tx(read_trace_tx: Transaction) -> str:
        return BitVMXTransactionsDTO.transaction_to_str(read_trace_tx)

    @field_serializer("trigger_read_challenge_tx", when_used="always")
    def serialize_trigger_read_challenge_tx(
        trigger_read_challenge_tx: Transaction,
    ) -> str:
        return BitVMXTransactionsDTO.transaction_to_str(trigger_read_challenge_tx)
