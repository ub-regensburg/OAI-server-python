from datetime import datetime

from typing import Optional
from flask import Request

from ..generated.models import OAIPMH, Error, ErrorCode

def create_error(error_code: ErrorCode, error_message) -> Error:

    error_data = {
        'code': error_code,
        'content': error_message
    }
    return Error.from_dict(error_data)

def create_base_response(request: Request, error: Optional[Error] = None) -> OAIPMH:
    request_attributes = {'content': request.base_url}
    if error is None or error.code not in [ErrorCode.BADARGUMENT, ErrorCode.BADVERB]:
        request_attributes = request_attributes | {key:value for (key, value) in request.args.items() if key in ["verb", "resumptionToken", "metadataPrefix", "from", "until", "set", "identifier"]}
    response_data = {
        'responseDate': datetime.now(),
        'request': request_attributes
    }

    return OAIPMH.from_dict(response_data)