import json


class Wallet:
    """DAO class for the Wallet"""

    address = None
    currency = None
    status = None
    file = None
    inferred = None

    def __init__(self, add: str, curr: str, f: str, u: int, i:bool = False) \
            -> None:
        self.address = add
        self.currency = curr
        self.file = f
        self.status = u
        self.inferred = i

    def __key(self):
        return self.address, self.currency

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other) -> bool:
        return \
            type(self) == type(other) and \
            self.__key() == other.__key()

    def __str__(self) -> str:
        return json.dumps(
            {
                "address": self.address if self.address is not None else ' ',
                "currency": self.currency if self.currency is not None else ' ',
                "status": self.status if self.status is not None else ' ',
                "inferred": self.inferred if self.inferred is not None else ' '
            },
            indent=2
        )
