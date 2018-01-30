from abc import ABCMeta, abstractmethod
from utility.async_requests import async_requests


class PersonalInfoRetriever:
    __metaclass__ = ABCMeta

    def retrieveInfo(self, accounts):
        reqs = []
        [reqs.append(self.formatURL(account.username))
         for account in accounts]
        return self.parseResults(async_requests(reqs))

    @abstractmethod
    def formatURL(self, url):
        pass

    @abstractmethod
    def parseResults(self, resuls):
        pass
