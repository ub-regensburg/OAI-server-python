from types import ModuleType
from typing import Optional

from ..shared.entity_creation import create_error
from ..shared.exceptions import NoSetHierarchyException
from ..generated.models import Error, ErrorCode, ListSets


def create_list_sets(plugin: ModuleType) -> ListSets:

    sets = plugin.create_sets()
    if not sets or len(sets) == 0:
        raise NoSetHierarchyException
    return ListSets(set=sets, resumptionToken=None)

def resume_list_sets(resumptionToken: str) -> ListSets | Error:
    return create_error(ErrorCode.BADRESUMPTIONTOKEN, 'Resumption tokens are not supported yet') # type: ignore

def response_or_error(plugin: ModuleType, resumption_token: Optional[str]) -> ListSets | Error:
    if resumption_token is not None:
        return resume_list_sets(resumption_token)

    try:
        return create_list_sets(plugin)
    except NoSetHierarchyException:
        return create_error(ErrorCode.NOSETHIERARCHY, f'This repository does not support sets') # type: ignore

    