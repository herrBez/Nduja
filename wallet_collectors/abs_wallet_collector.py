from abc import ABCMeta, abstractmethod
import json
import requests
import re


class Pattern:
    def __init__(self, format_object):
        self.pattern = re.compile(format_object["wallet_regexp"])
        self.name = format_object["name"]
        self.group = format_object["group"]
        self.symbol = format_object["symbol"]

    def match(self, content):
        matches = []
        if self.pattern.search(content):
            matches_iterator = self.pattern.finditer(content)

            matches = list(
                map(
                    lambda x:
                    (self.symbol, x.group()),
                    matches_iterator
                )
            )

        return matches


class AbsWalletCollector:
    '''Abstract base class for the Address Collector'''
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, format_file):
        self.format_object = json.loads(open(format_file).read())
        self.patterns = map(lambda f: Pattern(f), self.format_object)
    
    @abstractmethod
    def collect_address(self):
        '''Abstract method that must be returns a json '''

    def request_url(self, url, token = None):
        """ Request an url synchronously and returns the json response"""
        data = None
        if not token is None:
            data = {'Authorization': 'token ' + token}
        r = requests.get(url, headers=data)
        resp = r.text
        # ~ json.loads(resp) # if it is not well formatted exit
        return resp


pass
