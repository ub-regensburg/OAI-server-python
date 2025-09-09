from flask import request

from ..shared.entity_creation import create_error
from ..generated.models import Error, ErrorCode, Identify

def response_or_error(plugin) -> Identify | Error:
 
    if len([k for k in request.args.keys() if k not in ["verb"]]) != 0:
        return create_error(ErrorCode.BADARGUMENT, f'Request with verb "Identify" does not allow query parameters') # type: ignore

    return plugin.create_identify(request.base_url)
