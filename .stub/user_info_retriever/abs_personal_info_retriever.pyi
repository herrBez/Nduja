from abc import abstractmethod
from typing import Iterable
from typing import Any
from typing import List
from dao.personal_info import PersonalInfo
from dao.account import Account

class PersonalInfoRetriever:

    def retrieveInfo(self, accounts: Iterable[Any]) -> Any: ...

    @abstractmethod
    def formatURL(self, url: str) -> str: ...

    @abstractmethod
    def parseResults(self, results : List[Account]) -> List[PersonalInfo]: ...
