"""Module for string pattern matching"""
import re
from typing import List, Tuple, Dict


class Pattern:
    """Class that represent a pattern"""
    def __init__(self, format_object: Dict[str, str]) -> None:
        self._pattern = re.compile(format_object["wallet_regexp"])
        self._name = format_object["name"]
        self._group = format_object["group"]
        self._symbol = format_object["symbol"]

    @property
    def pattern(self):
        """Get pattern"""
        return self._pattern

    @pattern.setter
    def pattern(self, value):
        """Set pattern"""
        self._pattern = value

    @property
    def symbol(self) -> str:
        """Return the symbol of the currency"""
        return self._symbol

    @symbol.setter
    def symbol(self, value: str):
        """Set the symbol"""
        self._symbol = value

    @property
    def name(self) -> str:
        """Get the name"""
        return self._name

    @name.setter
    def name(self, value: str):
        """Set the name"""
        self._name = value

    def __str__(self) -> str:
        return self.symbol + " Pattern "

    def match(self, content: str) -> List[Tuple[str, str]]:
        """Returns matches of patter in a certain string"""
        matches_iterator = self.pattern.finditer(content)
        matches = [(self.symbol, x.group()) for x in matches_iterator]
        return matches


def match_email(text: str) -> List[str]:
    """Check if inside the text there is a list of emails"""
    pattern = re.compile(
        "\\b([a-zA-Z0-9_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)\\b")
    emails = pattern.findall(text)
    return emails


def match_personal_website(text: str) -> List[str]:
    """Check if inside the given text there is a list of websites"""
    pattern = re.compile("\\b(https?://([^/\\s]+/?)*)\\b")
    website_matches = pattern.findall(text)
    # Filter out all results that links to license reference
    website_matches = [w[0] for w in website_matches if
                       "license" not in w[0]]
    return website_matches
