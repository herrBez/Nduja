from abc import ABCMeta, abstractmethod
from typing import Optional, Dict, Tuple
import time


def get_epoch() -> int:
    return int(time.time())


class AbsTransactionRetriever:
    """Abstract base class for transaction retrievers"""
    __metaclass__ = ABCMeta
    timestamp_class = None  # type: Optional[int]

    @abstractmethod
    def get_input_output_addresses(self, address: str,
                                   timestamp: Optional[int] = None) -> \
            Tuple[Dict[str, int],  Dict[str, int], Dict[str, int]]:
        """Given an address it returns ALL transactions performed
        by the address"""
        pass

    @abstractmethod
    def get_currency(self) -> str:
        """Return the currency of the wallets that it retrieves"""
        pass
