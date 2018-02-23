import json
from typing import Dict


def print_json(s: Dict) -> None:
    """pretty print a json string"""
    print(json.dumps(s, indent=2))


def escape_utf8(text: str) -> str:
    return u''.join(text).encode('utf-8').strip()
