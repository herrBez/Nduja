from abc import ABCMeta, abstractmethod
from utility.async_requests import async_requests
from typing import Iterable, Any, List
from dao.personal_info import PersonalInfo
from dao.account import Account

class PersonalInfoRetriever:
    __metaclass__ = ABCMeta

    def retrieveInfo(self, accounts: List[Account]) -> List[PersonalInfo]:
        reqs = []
        for account in accounts:
            reqs.append(self.formatURL(account.username))

        return self.parseResults(async_requests(reqs))

    @abstractmethod
    def formatURL(self, username: str) -> str:
        pass

    @abstractmethod
    def parseResults(self, results: List[Account]) -> List[PersonalInfo]:
        pass
