from abc import ABCMeta, abstractmethod


class AbsAddressChecker:
    """Abstract base class for address checkers"""
    __metaclass__ = ABCMeta

    @abstractmethod
    def address_check(self, address: str) -> bool:
        """Abstract method that must be redefined, it must return True if the
        address is valid and findable, False otherwise"""
        pass

    @abstractmethod
    def address_valid(self, address: str) -> bool:
        """Abstract method that must be redefined, it must return True if the
        address is valid, False otherwise"""
        pass
