from datetime import datetime
from types import ModuleType
from typing import Optional

from ..shared.entity_creation import create_error
from ..shared.exceptions import NoRecordsMatchException
from ..generated.models import Error, ErrorCode, ListIdentifiers, MetadataPrefix

def create_list_identifiers(plugin: ModuleType, metadata_prefix: MetadataPrefix, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, set: Optional[str] = None) -> ListIdentifiers:

    headers = plugin.create_identifiers(metadata_prefix, start_date, end_date, set)
    if len(headers) == 0:
        raise NoRecordsMatchException()
    return ListIdentifiers(header=headers, resumptionToken=None)

def resume_list_identifiers(resumptionToken: str) -> ListIdentifiers | Error:
    return create_error(ErrorCode.BADRESUMPTIONTOKEN, 'Resumption tokens are not supported yet') # type: ignore

def response_or_error(plugin: ModuleType, resumption_token: Optional[str], metadata_prefix: Optional[str],  fr0m: Optional[str] = None, until: Optional[str] = None, set: Optional[str] = None) -> ListIdentifiers | Error:
    if metadata_prefix is None and resumption_token is None:
        return create_error(ErrorCode.BADARGUMENT, f'Request with verb "ListIdentifiers" requires exactly one of the following query parameters: "metadataPrefix" or "resumptionToken"') # type: ignore
    if metadata_prefix is not None and resumption_token is not None:
        return create_error(ErrorCode.BADARGUMENT, f'Request with verb "ListIdentifiers" can only have ONE of the following query parameters: "metadataPrefix" or "resumptionToken"') # type: ignore

    if resumption_token is not None:
        return resume_list_identifiers(resumption_token)

    if metadata_prefix is None:
        return create_error(ErrorCode.BADARGUMENT, 'Missing required query parameter: "metadataPrefix"') # type: ignore
    elif not any(x.value == metadata_prefix for x in MetadataPrefix):
        return create_error(ErrorCode.BADARGUMENT, f'Unknown value used for query parameter "metadataPrefix": {metadata_prefix}') # type: ignore
    start_date = end_date = None
    if fr0m is not None:
        try:
            start_date = datetime.fromisoformat(fr0m)
        except:
            return create_error(ErrorCode.BADARGUMENT, f'The following value is not a valid "from" datetime: "{fr0m}"') # type: ignore
    if until is not None:
        try:
            end_date = datetime.fromisoformat(until)
        except:
            return create_error(ErrorCode.BADARGUMENT, f'The following value is not a valid "until" datetime: "{until}"') # type: ignore

    try:
        return create_list_identifiers(plugin, MetadataPrefix(metadata_prefix), start_date, end_date, set) # type: ignore
    except NoRecordsMatchException:
        return create_error(ErrorCode.NORECORDSMATCH, f'No identifiers in the repository match the selected criteria') # type: ignore

    