import json
from typing import Dict


def print_json(s: Dict) -> None:
    """pretty print a json string"""
    print(json.dumps(s, indent=2))
