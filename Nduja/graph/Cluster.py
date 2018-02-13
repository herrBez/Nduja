from typing import Iterable
from dao.wallet import Wallet

class Cluster:

    def __init__(self, address: Wallet, addresses: Iterable[Wallet] = []) -> None:
        self._original_address = address
        self._address_set = set(addresses)
        self._address_set.add(address)

    @property
    def original_address(self) -> Wallet:
        return self._original_address

    @property
    def address_set(self) -> Iterable[Wallet]:
        return self._address_set
