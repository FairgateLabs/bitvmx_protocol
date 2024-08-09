from dependency_injector import providers

from verifier_app.persistence.json.bitvmx_protocol_verifier_dto_json_persistence import (
    BitVMXProtocolVerifierDTOJsonPersistence,
)


class BitVMXProtocolVerifierDTOPersistences:
    json = providers.Singleton(BitVMXProtocolVerifierDTOJsonPersistence, base_path="verifier_files")

    bitvmx = json
