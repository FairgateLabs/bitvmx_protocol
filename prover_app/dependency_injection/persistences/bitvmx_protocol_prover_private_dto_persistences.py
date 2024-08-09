from dependency_injector import providers

from prover_app.persistence.json.bitvmx_protocol_prover_private_dto_json_persistence import (
    BitVMXProtocolProverPrivateDTOJsonPersistence,
)


class BitVMXProtocolProverPrivateDTOPersistences:
    json = providers.Singleton(
        BitVMXProtocolProverPrivateDTOJsonPersistence, base_path="prover_files"
    )

    bitvmx = json
