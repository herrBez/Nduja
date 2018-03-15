"""Module with utilities for printing"""
from typing import Dict
import json


def print_json(json_dict: Dict) -> None:
    """pretty print a json string"""
    print(json.dumps(json_dict, indent=2))


def escape_utf8(text: str) -> bytes:
    """escaping non utf8 chars"""
    return u''.join(text).encode('utf-8').strip()
