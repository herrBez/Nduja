from typing import Iterable, Optional
from typing import Set
from typing import Any
from typing import List

from dao.wallet import Wallet
from graph.abs_transaction_retriever import AbsTransactionRetriever


class Cluster:
    """Class that represents the Wallet that are belonging (or are supposed to
    belong) to a person, i.e., addresses that are inputs of the same transaction
    """

    def __init__(self,
                 addresses: Iterable[Wallet],
                 transaction_retriever: Optional[AbsTransactionRetriever],
                 inferred_addresses: Iterable[Wallet] = [],
                 ids: Iterable[int] = [-1]) -> None:
        self._original_addresses = set(addresses)
        self._inferred_addresses = set(inferred_addresses)
        for w in self._original_addresses:
            self._inferred_addresses.add(w)
        self.filled = False
        self.accounts = []  # type: List[int]
        self._belongs_to_blacklist = False
        self._ids = set(ids)
        self._transaction_retriever = transaction_retriever

    @property
    def ids(self):
        return self._ids

    @property
    def belongsToBlackList(self) -> bool:
        return self._belongs_to_blacklist

    @property
    def original_addresses(self) -> Set[Wallet]:
        return self._original_addresses

    @property
    def inferred_addresses(self) -> Set[Wallet]:
        return self._inferred_addresses

    def add_inferred_address(self, address: Wallet):
        self._inferred_addresses.add(address)

    def merge_original_list(self, other: 'Cluster'):
        self.original_addresses.update(other.original_addresses)

    def merge(self, other: 'Cluster') -> None:
        self._original_addresses = self.original_addresses.union(other.original_addresses)
        self._inferred_addresses = self.inferred_addresses.union(other.inferred_addresses)
        self._ids = self._ids.union(other.ids)

    def __hash__(self):
        return hash(frozenset(self._inferred_addresses))

    def __eq__(self, other) -> bool:
        return type(self) == type(other) and \
               self._inferred_addresses == other.inferred_addresses

    def __str__(self) -> str:
        return str(list(self._original_addresses)) + "\n" + \
               str(list(self._inferred_addresses))

    def intersect(self, other: 'Cluster') -> bool:
        return len(self.inferred_addresses.
                   intersection(other.inferred_addresses)) > 0

    def fill_cluster(self, black_list: 'Cluster') -> bool:
        """
        This function fills the cluster by finding all the siblings, i.e.,
        addresses that belongs (or are supposed to belong) to a single physical
        person.
        Fill cluster is an expensive operation. Therefore it should be done
        only once. Indeed it requires a time proportional to the number
        of inferred addresses * their transactions"""
        if not self.filled:
            stack = set([])
            tmp_black_list = []
            for saddr in self.inferred_addresses:
                stack.add(saddr)

            while len(stack) > 0 and len(self.inferred_addresses) < 30:
                elem = stack.pop()
                self.add_inferred_address(elem)
                
                if elem in black_list.inferred_addresses:
                    black_list.merge(self)
                    self.filled = True
                    self._belongs_to_blacklist = True
                    return False

                tmp_black_list.append(elem)
                a, b, siblings = self._transaction_retriever. \
                    get_input_output_addresses(elem.address)
                for s in siblings:
                    w = Wallet(s, self._transaction_retriever.get_currency(),
                               "", 1, True)
                    if w not in black_list.inferred_addresses \
                            and w not in tmp_black_list:
                        stack.add(w)

            self.filled = True
        return True

