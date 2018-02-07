import json


class Wallet:
    """DAO class for the Wallet"""

    address = None
    currency = None
    status = None
    file = None

    def __init__(self, add: str, curr: str, f: str, u: int) -> None:
        self.address = add
        self.currency = curr
        self.file = f
        self.status = u

    def __str__(self) -> str:
        return json.dumps(
            {
                "address": self.address if self.address is not None else ' ',
                "currency": self.currency if self.currency is not None else ' ',
                "status": self.status if self.status is not None else ' '
            },
            ident=2
        )
