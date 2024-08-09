from dependency_injector import providers

from prover_app.persistence.json.bitvmx_protocol_prover_dto_json_persistence import (
    BitVMXProtocolProverDTOJsonPersistence,
)


class BitVMXProtocolProverDTOPersistences:
    json = providers.Singleton(BitVMXProtocolProverDTOJsonPersistence, base_path="prover_files")

    bitvmx = json
