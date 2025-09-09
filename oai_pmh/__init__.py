from flask import Flask


APP = Flask(__name__)


from .routes import oai
from .routes import identify
from .routes import get_record
from .routes import list_records
from .routes import list_identifiers
from .routes import list_metadata_formats
from .routes import list_sets
