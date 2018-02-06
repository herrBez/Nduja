from abc import abstractmethod
from typing import Iterable
from typing import Any


class PersonalInfoRetriever:

    def retrieveInfo(self, accounts: Iterable[Any]) -> Any: ...

    @abstractmethod
    def formatURL(self, url: str) -> str: ...

    @abstractmethod
    def parseResults(self, results : Any) -> Any: ...
