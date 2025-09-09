from types import ModuleType

from ..shared.entity_creation import create_error
from ..shared.exceptions import CannotDissemintateFormatException, IDDoesNotExistException
from ..generated.models import Error, ErrorCode, GetRecord, MetadataPrefix


def create_get_record(plugin: ModuleType, identifier: str, metadata_prefix: MetadataPrefix) -> GetRecord:
    record = plugin.create_record(identifier, metadata_prefix)
    return GetRecord(record=record)

def response_or_error(plugin: ModuleType, identifier: str | None, metadata_prefix: str | None) -> GetRecord | Error:

    if identifier is None:
        return create_error(ErrorCode.BADARGUMENT, 'Missing required query parameter: "identifier"') # type: ignore
    if metadata_prefix is None:
        return create_error(ErrorCode.BADARGUMENT, 'Missing required query parameter: "metadataPrefix"') # type: ignore
    elif not any(x.value == metadata_prefix for x in MetadataPrefix):
        return create_error(ErrorCode.BADARGUMENT, f'Unknown value used for query parameter "metadataPrefix": {metadata_prefix}') # type: ignore

    try:
        return create_get_record(plugin, identifier, MetadataPrefix(metadata_prefix))
    except IDDoesNotExistException:
        return create_error(ErrorCode.IDDOESNOTEXIST, f'Record with identifier "{identifier}" does not exist') # type: ignore
    except CannotDissemintateFormatException:
        return create_error(ErrorCode.CANNOTDISSEMINATEFORMAT, f'The metadata schema "{identifier}" is not available for this record') # type: ignore
    