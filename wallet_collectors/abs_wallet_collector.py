from abc import ABCMeta, abstractmethod
import json
# N.B. According to this issue we should import grequests before! requests
# otherwise grequets does not work
# https://github.com/kennethreitz/grequests/issues/103
import grequests
import requests
import re
from functools import reduce
import traceback
import sys
import logging

from typing import List
from typing import Tuple
from typing import Any
from typing import Dict

from typing import TypeVar


class Pattern:

    def __init__(self, format_object: Dict[str, str]) -> None:
        self.pattern = re.compile(format_object["wallet_regexp"])
        self.name = format_object["name"]
        self.group = format_object["group"]
        self.symbol = format_object["symbol"]

    @property
    def symbol(self) -> str: return self.symbol

    @property
    def name(self) -> str: return self.name

    def __str__(self) -> str:
        return self.symbol + " Pattern "

    def match(self, content: str) -> List[Tuple[str, str]]:
        matches_iterator = self.pattern.finditer(content)
        matches = list(
            map(
                lambda x:
                (self.symbol, x.group()),
                matches_iterator
            )
        )
        return matches


def match_email(text: str) -> List[str]:
    """Check if inside the text there is a list of emails"""
    pattern = re.compile("\\b([a-zA-Z0-9_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)\\b")
    emails = pattern.findall(text)
    return emails


def match_personal_website(text: str) -> List[str]:
    """Check if inside the given text there is a list of websites"""
    pattern = re.compile("\\b(https?://([^/\\s]+/?)*)\\b")
    website_matches = pattern.findall(text)
    # Filter out all results that links to license reference
    website_matches = [w[0] for w in website_matches if "license" not in w[0]]
    return website_matches

T = TypeVar('T')
def flatten(l : List[List[T]]) -> List[T]:
    """It takes as input a list of lists and returns a list"""
    return reduce(
        lambda x, y: x + y,
        l,
        []
    )


class AbsWalletCollector:
    """Abstract base class for the Address Collector"""
    __metaclass__ = ABCMeta

    def __init__(self, format_file: str) -> None:
        self.format_object = json.loads(open(format_file).read())
        self.patterns = list(map(lambda f: Pattern(f), self.format_object))

    @property
    def patterns(self) -> List[Pattern]: return self.patterns

    def request_url(self, url: str, token: str=None) -> str:
        """ Request an url synchronously and returns the json response"""
        data = None
        if token is not None:
            data = {'Authorization': 'token ' + token}
        r = requests.get(url, headers=data)
        resp = r.text
        # ~ json.loads(resp) # if it is not well formatted exit
        return resp

    @abstractmethod
    def collect_raw_result(self, queries: List[str]) -> List[Any]:
        '''Abstract method that must be returns a json '''

    @abstractmethod
    def construct_queries(self) -> List[str]:
        '''Given an object of type Pattern creates a query for the particular
        instance'''

    @abstractmethod
    def extract_content(self, response: List[Any]) -> List[str]:
        '''Given a raw response it returns the string to match with the
        patterns'''

    @abstractmethod
    def build_answer_json(self, raw_response: Any, content: str,
                          match_list, symbol_list, wallet_list, emails=None,
                          websites=None) -> Dict[str, Any]:
        '''Build the answer json using the response as given by the
        server and the list of symbol_list and wallet_list'''

    def collect_address(self) -> str:
        final_result = []

        queries = self.construct_queries()
        logging.debug("Queries Constructed")

        raw_results = self.collect_raw_result(queries)
        logging.debug("Raw Results Collected")

        contents = self.extract_content(raw_results)
        logging.debug("Contents extracted")

        for i in range(len(contents)):
            if contents[i] != "":
                try:

                    emails = match_email(contents[i])
                    websites = match_personal_website(contents[i])

                    # Retrieve the list of matches
                    match_list = \
                        flatten(
                            list(
                                map(lambda x:
                                    x.match(contents[i]), self.patterns)
                            )
                        )

                    # A match was found
                    if len(match_list) > 0:
                        match_list = list(set(match_list))
                        symbol_list, wallet_list = map(list, zip(*match_list))

                        element = self.build_answer_json(raw_results[i],
                                                         contents[i],
                                                         symbol_list,
                                                         wallet_list,
                                                         emails,
                                                         websites)

                        final_result.append(element)

                except Exception:
                    traceback.print_exc()
                    print("Error on: ", file=sys.stderr)
            else:
                logging.warning("content[" + str(i) + "] empty")

            logging.debug(str(i) + "/" + str(len(contents))
                          + " elements processed.")

        return '{"results" : ' + str(json.dumps(final_result)) + '}'



