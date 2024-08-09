from dependency_injector import providers

from verifier_app.persistence.json.bitvmx_protocol_verifier_private_dto_json_persistence import (
    BitVMXProtocolVerifierPrivateDTOJsonPersistence,
)


class BitVMXProtocolVerifierPrivateDTOPersistences:
    json = providers.Singleton(
        BitVMXProtocolVerifierPrivateDTOJsonPersistence, base_path="verifier_files"
    )

    bitvmx = json
