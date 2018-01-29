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


class Pattern:
    def __init__(self, format_object):
        self.pattern = re.compile(format_object["wallet_regexp"])
        self.name = format_object["name"]
        self.group = format_object["group"]
        self.symbol = format_object["symbol"]

    def __str__(self):
        return self.symbol + " Pattern "

    def match(self, content):
        matches_iterator = self.pattern.finditer(content)
        matches = list(
            map(
                lambda x:
                (self.symbol, x.group()),
                matches_iterator
            )
        )
        return matches


def print_json(s):
    print(json.dumps(s, indent=2))


def flatten(l) -> list:
    '''It takes as input a list of lists and returns a list'''
    return reduce(
        lambda x, y: x + y,
        l,
        []
    )


class AbsWalletCollector:
    '''Abstract base class for the Address Collector'''
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, format_file):
        self.format_object = json.loads(open(format_file).read())
        self.patterns = list(map(lambda f: Pattern(f), self.format_object))

    def request_url(self, url, token=None):
        """ Request an url synchronously and returns the json response"""
        data = None
        if token is not None:
            data = {'Authorization': 'token ' + token}
        r = requests.get(url, headers=data)
        resp = r.text
        # ~ json.loads(resp) # if it is not well formatted exit
        return resp

    @abstractmethod
    def collect_raw_result(self, queries) -> list:
        '''Abstract method that must be returns a json '''

    @abstractmethod
    def construct_queries(self, pattern) -> list:
        '''Given an object of type Pattern creates a query for the particular
        instance'''

    @abstractmethod
    def extract_content(self, response) -> str:
        '''Given a raw response it returns the string to match with the
        patterns'''

    @abstractmethod
    def build_answer_json(self, raw_response, content,
                          match_list, symbol_list, wallet_list):
        '''Build the answer json using the response as given by the
        server and the list of symbol_list and wallet_list'''

    def collect_address(self):
        final_result = []

        queries = self.construct_queries()

        list_of_raw_result = self.collect_raw_result(queries)

        raw_result = flatten(list_of_raw_result)

        for r in raw_result:

            content = self.extract_content(r)

            try:
                # Retrieve the list of matches
                match_list = list(
                    map(lambda x:
                        x.match(content), self.patterns)
                )
                # Reduce the list of lists to a single list
                match_list = reduce(
                    lambda x, y: x + y,
                    match_list,
                    []
                )
                # A match was found
                if len(match_list) > 0:
                    symbol_list, wallet_list = map(list, zip(*match_list))
                    element = self.build_answer_json(r,
                                                     content,
                                                     symbol_list,
                                                     wallet_list)

                    final_result = final_result + [element]


            except Exception:
                traceback.print_exc()
                print("Error on: ", file=sys.stderr)
        return '{"results" : ' + str(json.dumps(final_result)) + '}'


pass
