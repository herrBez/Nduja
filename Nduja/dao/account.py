import json


class Account:
    """DAO class for an account in the database"""

    ID = None
    host = None
    username = None
    info = None

    def __init__(self, ID: str, host: str, username: str, info: str) -> None:
        self.ID = ID
        self.host = host
        self.username = username
        self.info = info

    def __str__(self) -> str:
        return json.dumps(
            {
                "id": str(self.ID) if self.ID is not None else ' ',
                "host": self.host if self.host is not None else ' ',
                "username": str(self.username) if self.username is not None
                else ' ',
                "info": str(self.info) if self.info is not None else ' '
            },
            ident=2
        )
