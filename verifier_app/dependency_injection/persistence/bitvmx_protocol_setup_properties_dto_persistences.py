from dependency_injector import providers

from verifier_app.persistence.json.bitvmx_protocol_setup_properties_dto_json_persistence import (
    BitVMXProtocolSetupPropertiesDTOJsonPersistence,
)


class BitVMXProtocolSetupPropertiesDTOPersistences:
    json = providers.Singleton(
        BitVMXProtocolSetupPropertiesDTOJsonPersistence, base_path="verifier_files"
    )

    bitvmx = json
