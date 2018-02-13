from typing import Iterable

from dao.wallet import Wallet

from . import Cluster as Cluster_Type

class Cluster:

    def __init__(self,
                 addresses: Iterable[Wallet],
                 inferred_addresses: Iterable[Wallet] = []) -> None:
        self._original_addresses = set(addresses)
        self._inferred_addresses = set(inferred_addresses)
        for w in self._original_addresses:
            self._inferred_addresses.add(w)

    @property
    def original_address(self) -> Wallet:
        return self._original_addresses

    @property
    def inferred_addresses(self) -> Iterable[Wallet]:
        return self._inferred_addresses

    def merge(self, other: Cluster_Type) -> Cluster_Type:
        originals = self.original_address.union(other.original_address)
        inferred = self.inferred_addresses.union(other.inferred_addresses)
        return Cluster(originals, inferred)

