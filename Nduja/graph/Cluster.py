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

    def add_inffered_address(self, address: Wallet):
        self._inferred_addresses.add(address)

    def merge_original_list(self, other: Cluster_Type):
        self.original_address.update(other.original_address)

    def merge(self, other: Cluster_Type) -> Cluster_Type:
        originals = self.original_address.union(other.original_address)
        inferred = self.inferred_addresses.union(other.inferred_addresses)
        return Cluster(originals, inferred)

    def __hash__(self):
        return hash(frozenset(self._inferred_addresses))

    def __eq__(self, other) -> bool:
        return type(self) == type(other) and \
               self._inferred_addresses == other.inferred_addresses

    def __str__(self) -> str:
        return str(list(self._original_addresses)) + "\n" + \
               str(list(self._inferred_addresses))
