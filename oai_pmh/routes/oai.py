from io import BytesIO
from types import ModuleType
from typing import Optional
from flask import redirect, render_template, make_response, request, url_for, send_file
from xmlschema import XMLSchema

from . import identify, get_record, list_records, list_identifiers, list_metadata_formats, list_sets

from ..shared.entity_creation import create_base_response, create_error
from ..shared.plugin_handler import get_plugin
from .. import APP
from ..generated.models import Error, ErrorCode, MetadataPrefix, Verb, ListIdentifiers, ListRecords, ListMetadataFormats, ListSets, GetRecord, Identify, OAIListIdentifiers, OAIListRecords, OAIListMetadataFormats, OAIListSets, OAIGetRecord, OAIIdentify, OAIPMH

GenericOAIObject = ListIdentifiers | ListRecords | ListMetadataFormats | ListSets | GetRecord | Identify
GenericOAIResponse = OAIListIdentifiers | OAIListRecords | OAIListMetadataFormats | OAIListSets | OAIGetRecord | OAIIdentify | OAIPMH

@APP.route("/")
def redirect_root():
    return redirect(url_for('redirect_source_root', source='default'))

@APP.route("/<source>/")
def redirect_source_root(source: str):
    if source not in ['favicon.ico']:
        return redirect(f'/{source}/oai?verb=Identify')
    return make_response('Not Found', 404)

@APP.route("/<source>/oai")
def oai_get(source: str):

    plugin = get_plugin(source)
    verb = request.args.get('verb')
    resumption_token = request.args.get('resumptionToken')
    metadata_prefix = request.args.get('metadataPrefix')

    identifier = request.args.get('identifier')

    fr0m = request.args.get('from')
    until = request.args.get('until')
    s3t = request.args.get('set')


    result = response_or_error(plugin, verb, resumption_token, metadata_prefix, identifier, fr0m, until, s3t)

    if isinstance(result, Error):
        base_response = create_base_response(request, result)
    else:
        base_response = create_base_response(request)

    response_data = create_oai_response(result, base_response)

    template = render_template(get_template(result), oai_response=response_data) # type: ignore
    # schema = XMLSchema('https://www.openarchives.org/OAI/2.0/OAI-PMH.xsd', build=False)
    # schema.add_schema('https://www.openarchives.org/OAI/2.0/oai_dc.xsd')
    # schema.add_schema('https://www.dublincore.org/schemas/xmls/qdc/dc.xsd')
    # schema.build()
    # schema.validate(template)
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'

    return response

def get_template(result: GenericOAIObject | Error) -> str:
    if isinstance(result, Identify):
        return 'identify.xml.jinja'
    elif isinstance(result, GetRecord):
        return 'get-record.xml.jinja'
    elif isinstance(result, ListIdentifiers):
        return 'list-identifiers.xml.jinja'
    elif isinstance(result, ListRecords):
        return 'list-records.xml.jinja'
    elif isinstance(result, ListSets):
        return 'list-sets.xml.jinja'
    elif isinstance(result, ListMetadataFormats):
        return 'list-metadata-formats.xml.jinja'
    elif isinstance(result, Error):
        return 'oai-pmh.xml.jinja'
    else:
        return 'oai-pmh.xml.jinja'

def create_oai_response(result: GenericOAIObject | Error, base_response: OAIPMH) -> GenericOAIResponse:
    if isinstance(result, GetRecord):
        return OAIGetRecord.from_dict(base_response.to_dict() | {'GetRecord': result.to_dict()})
    elif isinstance(result, Identify):
        return OAIIdentify.from_dict(base_response.to_dict() | {'Identify': result.to_dict()})
    elif isinstance(result, ListRecords):
        return OAIListRecords.from_dict(base_response.to_dict() | {'ListRecords': result.to_dict()})
    elif isinstance(result, ListIdentifiers):
        return OAIListIdentifiers.from_dict(base_response.to_dict() | {'ListIdentifiers': result.to_dict()})
    elif isinstance(result, ListSets):
        return OAIListSets.from_dict(base_response.to_dict() | {'ListSets': result.to_dict()})
    elif isinstance(result, ListMetadataFormats):
        return OAIListMetadataFormats.from_dict(base_response.to_dict() | {'ListMetadataFormats': result.to_dict()})
    elif isinstance(result, Error):
        base_response.error = result
        return base_response
    else:
        return base_response

def create_oai_object(plugin: ModuleType, verb: Verb, resumption_token: Optional[str], metadata_prefix: Optional[MetadataPrefix],  identifier: Optional[str], fr0m: Optional[str] = None, until: Optional[str] = None, set: Optional[str] = None) -> GenericOAIObject | Error:
    if verb == Verb.IDENTIFY:
        return identify.response_or_error(plugin)
    elif verb == Verb.GETRECORD:
        return get_record.response_or_error(plugin, identifier, metadata_prefix)
    elif verb == Verb.LISTRECORDS:
        return list_records.response_or_error(plugin, resumption_token, metadata_prefix, fr0m, until, set)
    elif verb == Verb.LISTIDENTIFIERS:
        return list_identifiers.response_or_error(plugin, resumption_token, metadata_prefix, fr0m, until, set)
    elif verb == Verb.LISTSETS:
        return list_sets.response_or_error(plugin, resumption_token)
    elif verb == Verb.LISTMETADATAFORMATS:
        return list_metadata_formats.response_or_error(plugin, identifier)
    else:
        return create_error(ErrorCode.BADVERB, f'The Server did not process the query parameter "verb" correctly. The processed value is "{verb}"') # type: ignore

def response_or_error(plugin: ModuleType, verb: Optional[str], resumption_token: Optional[str], metadata_prefix: Optional[str], identifier: Optional[str], fr0m: Optional[str] = None, until: Optional[str] = None, s3t: Optional[str] = None) -> GenericOAIObject | Error:

    undefined_params = set([*request.args.keys()]) - set(['verb', 'resumptionToken', 'metadataPrefix', 'identifier', 'from', 'until', 'set'])
    if bool(undefined_params):
        return create_error(ErrorCode.BADARGUMENT, f'The following query parameters are not supported: {", ".join(undefined_params)}') # type: ignore
    if verb is None:
        return create_error(ErrorCode.BADVERB, 'Missing required query parameter: "verb"') # type: ignore
    elif not any(x.value == verb for x in Verb):
        return create_error(ErrorCode.BADVERB, f'Invalid value used for query parameter "verb": {verb}') # type: ignore

    return create_oai_object(plugin, Verb(verb), resumption_token, metadata_prefix, identifier, fr0m, until, s3t) # type: ignore