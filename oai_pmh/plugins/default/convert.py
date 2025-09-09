from datetime import datetime
import json
import pathlib
from random import randint, choice
from typing import Any, Optional

from ...shared.exceptions import IDDoesNotExistException, NoMetadataFormatsException, NoRecordsMatchException

from ...generated.models import DublinCoreMetadata, Header, MetadataPrefix, Record, RecordMetadata, MetadataFormat, Set, Identify



def create_record_metadata(metadata: Optional[dict[str, Any]], metadata_prefix: MetadataPrefix) -> RecordMetadata:
    # dublincore_metadata = DublinCoreMetadata(\
    #     title= ['Using Structural Metadata to Localize Experience of Digital Content']\
    #     creator= ['Dushay, Naomi']\
    #     subject= ['Digital Libraries']\
    #     description= ['With the increasing technical sophistication of both information consumers and providers, there is increasing demand for more meaningful experiences of digital information. We present a framework that separates digital object experience, or rendering, from digital object storage and manipulation, so the rendering can be tailored to particular communities of users.', 'Comment: 23 pages including 2 appendices, 8 figures']\
    #     date= ['2001-12-14']\
    #     )
    if metadata is None:
        metadata = {
            'title': ['Using Structural Metadata to Localize Experience of Digital Content'],
            'creator': ['Dushay, Naomi'],
            'subject': ['Digital Libraries'],
            'description': ['With the increasing technical sophistication of both information consumers and providers, there is increasing demand for more meaningful experiences of digital information. We present a framework that separates digital object experience, or rendering, from digital object storage and manipulation, so the rendering can be tailored to particular communities of users.', 'Comment: 23 pages including 2 appendices, 8 figures'],
            'date': ['2001-12-14']
        }
    return RecordMetadata(dublincore=DublinCoreMetadata.from_dict(metadata))

def create_header(identifier: str, datestamp: datetime, deleted: Optional[bool] = False, set: Optional[list[str]] = None) -> Header:
    return Header(identifier=identifier, datestamp=datestamp, setSpec=set or None, status="deleted" if deleted else None)

def create_record(identifier: str, metadata_prefix: MetadataPrefix) -> Record:
    has_body = randint(1,7) % 7 != 0
    header = create_header(identifier, datetime(randint(1970, 2022), randint(1,12), randint(1, 28)), deleted=not has_body)
    record = Record(header=header)
    if has_body:
        record.metadata = create_record_metadata(None, metadata_prefix)
        if randint(1,5) % 5 == 0:
            record.about = '<oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/ http://www.openarchives.org/OAI/2.0/oai_dc.xsd"> <dc:publisher>Los Alamos arXiv</dc:publisher> <dc:rights>Metadata may be used without restrictions as long as the oai identifier remains attached to it.</dc:rights> </oai_dc:dc>'
    return record
    
def create_records(metadata_prefix: MetadataPrefix, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, set: Optional[str] = None) -> list[Record]:
    if set is not None:
        if set not in [set.set_spec for set in create_sets()]:
            raise NoRecordsMatchException()
        filestream = open (f'{pathlib.Path(__file__).parent.resolve()}/{set}.json', "r")
        data = json.loads(filestream.read())
        return [Record(header=create_header(x.get("identifier"), datetime.strptime(x.get('datestamp'), "%Y-%m-%d")), metadata=create_record_metadata(x.get('metadata'), metadata_prefix)) for x in data]
    else:
        records = [create_record(str(randint(100_000_000, 1_000_000_000)), metadata_prefix) for x in range(1, randint(1,100))]
        if start_date is not None:
            records = [x for x in records if x.header.datestamp >= start_date]
        if end_date is not None:
            records = [x for x in records if x.header.datestamp <= end_date]
        return records

def create_identifiers(metadata_prefix: MetadataPrefix, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, set: Optional[str] = None) -> list[Header]:
    if set is not None:
        if set not in [set.set_spec for set in create_sets()]:
            raise NoRecordsMatchException()
        filestream = open (f'{pathlib.Path(__file__).parent.resolve()}/{set}.json', "r")
        data = json.loads(filestream.read())
        return [create_header(x.get("identifier"), datetime.strptime(x.get('datestamp'), "%Y-%m-%d")) for x in data]
    else:
        headers = [
                create_header(str(randint(100_000_000, 1_000_000_000)),
                datetime(randint(1970, 2022), randint(1,12), randint(1, 28)),
                deleted=randint(1,7) % 7 == 0
            ) for x in range(1, randint(1,100))]
        if start_date is not None:
            headers = [x for x in headers if x.datestamp >= start_date]
        if end_date is not None:
            headers = [x for x in headers if x.datestamp <= end_date]
        return headers

def create_metadata_formats(identifier: str | None) -> list[MetadataFormat]:
    if identifier is None:
        return [MetadataFormat(metadataPrefix=MetadataPrefix.OAI_DC, metadataNamespace="http://www.openarchives.org/OAI/2.0/oai_dc/", schema="http://www.openarchives.org/OAI/2.0/oai_dc.xsd")] # type: ignore
    return create_metadata_formats_for_record(identifier)

def create_metadata_formats_for_record(identifier: str | None) -> list[MetadataFormat]:
    if choice([True,True,True,True,True,True,True,True,False]):
        return [MetadataFormat(metadataPrefix=MetadataPrefix.OAI_DC, metadataNamespace="http://www.openarchives.org/OAI/2.0/oai_dc/", schema="http://www.openarchives.org/OAI/2.0/oai_dc.xsd")] # type: ignore
    if choice([True,True,True,True,True,True,True,True,False]):
        raise NoMetadataFormatsException
    raise IDDoesNotExistException

def create_sets() -> list[Set]:
    sets = [
        ("parent", "Parent IEs", "Structural IEs that contain other IEs, but no content themselves"),
        ("content", "Content IEs", "IEs that contain content and possibly are part of a parent IE")
    ]
    return [Set(setSpec=spec, setName=name, setDescription=desc) for (spec, name, desc) in sets]

def create_identify(url) -> Identify:
    return Identify.from_dict({
        'baseURL': url,
        'adminEmail': ["sysadmin@example.de", "admin@example.de"],
        'granularity': "YYYY-MM-DD",
        'repositoryName': "Test Repository",
        "protocolVersion": "2.0",
        "deletedRecord": 'transient',
        'earliestDatestamp': datetime(1970, 1, 1),
        "compression": ["gzip", "br"],
        'description': ["A OAI-PMH test server"]
    }) # type: ignore