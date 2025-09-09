from types import ModuleType

from ..shared.entity_creation import create_error
from ..shared.exceptions import IDDoesNotExistException, NoMetadataFormatsException
from ..generated.models import Error, ErrorCode, ListMetadataFormats


def create_list_metadata_formats(plugin: ModuleType, identifier: str | None) -> ListMetadataFormats:
    metadata_formats = plugin.create_metadata_formats(identifier)
    return ListMetadataFormats(metadataFormat=metadata_formats)

def response_or_error(plugin: ModuleType, identifier: str | None) -> ListMetadataFormats | Error:

    try:
        return create_list_metadata_formats(plugin, identifier)
    except IDDoesNotExistException:
        return create_error(ErrorCode.IDDOESNOTEXIST, f'Record with identifier "{identifier}" does not exist') # type: ignore
    except NoMetadataFormatsException:
        return create_error(ErrorCode.NOMETADATAFORMATS, f'No metadata schema found for record "{identifier}"') # type: ignore
    