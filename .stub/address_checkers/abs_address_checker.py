from abc import abstractmethod



class AbsAddressChecker:
    @abstractmethod
    def address_check(self, address: str) -> bool: ...

    @abstractmethod
    def address_valid(self, address: str) -> bool: ...
