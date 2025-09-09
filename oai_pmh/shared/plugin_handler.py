import importlib
from types import ModuleType

def get_plugin(source: str) -> ModuleType:
    return importlib.import_module(f'.plugins.{source}.convert', 'oai_pmh')