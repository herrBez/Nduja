"""Module with base class for wallet collectors"""
from typing import Any, Optional, List, Dict, TypeVar

from abc import ABCMeta, abstractmethod
import json
from functools import reduce
import traceback
import logging

import requests
from requests import Response


from utility.pattern import Pattern
from utility.pattern import match_personal_website
from utility.pattern import match_email
from utility.print_utility import escape_utf8

T = TypeVar('T')


def flatten(li_: List[List[T]]) -> List[T]:
    """It takes as input a list of lists and returns a list"""
    return reduce(
        lambda x, y: x + y,
        li_,
        []
    )


class AbsWalletCollector:
    """Abstract base class for the Address Collector"""
    __metaclass__ = ABCMeta

    def __init__(self, format_file: str,  progress_bar_position: int) -> None:
        self.progress_bar_position = progress_bar_position
        self._format_object = json.loads(open(format_file).read())
        self._patterns = [Pattern(f) for f in self._format_object]

    @property
    def patterns(self) -> List[Pattern]:
        """Return a list of patterns"""
        return self._patterns

    @patterns.setter
    def patterns(self, value: List[Pattern]) -> None:
        """Set a list of patterns"""
        self._patterns = value

    def request_url(self, url: str, token: str = None) -> Optional[Response]:
        """ Request an url synchronously and returns the json response"""
        data = None
        if token is not None:
            data = {'Authorization': 'token ' + token}
        try:
            response = requests.get(url, headers=data)
        except requests.exceptions.MissingSchema:
            response = None
            # traceback.print_exc()
        return response

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
                          symbol_list: List[str],
                          wallet_list: List[str],
                          emails: Optional[List[str]] = None,
                          websites: Optional[List[str]] = None)\
            -> Dict[str, Any]:
        '''Build the answer json using the response as given by the
        server and the list of symbol_list and wallet_list'''

    def collect_address(self) -> str:
        """Method to collect addresses"""
        final_result = []

        queries = self.construct_queries()
        logging.debug("Queries Constructed")

        raw_results = self.collect_raw_result(queries)
        logging.debug("Raw Results Collected")

        contents = self.extract_content(raw_results)
        logging.debug("Contents extracted")

        for i in range(len(contents)):
            contents[i] = bytes(contents[i], 'utf-8').decode('utf-8', 'ignore')

            if contents[i] != "":
                try:
                    logging.debug("%s\n%s\n%s\n",
                                  "***",
                                  escape_utf8(contents[i]),
                                  "***")
                    emails = match_email(contents[i])
                    websites = match_personal_website(contents[i])

                    # Retrieve the list of matches
                    match_list = \
                        flatten(
                            [x.match(contents[i]) for x in self.patterns]
                        )

                    # A match was found
                    if match_list:
                        match_list = list(set(match_list))
                        logging.debug(str(match_list))
                        tmp_list = list(zip(*match_list))
                        logging.debug(str(tmp_list))
                        symbol_list = tmp_list[0]
                        wallet_list = tmp_list[1]

                        element = self.build_answer_json(raw_results[i],
                                                         contents[i],
                                                         symbol_list,
                                                         wallet_list,
                                                         emails,
                                                         websites)

                        final_result.append(element)

                except Exception:
                    logging.error("Error on: %s", str(traceback.format_exc()))
            else:
                logging.warning("content[%d] empty", i)

            logging.debug("%d/%d elements processed", i+1, len(contents))

        return '{"results" : ' + str(json.dumps(final_result)) + '}'
