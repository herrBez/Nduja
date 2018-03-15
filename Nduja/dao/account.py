"""Module for Account DAO"""
import json


class Account:
    """DAO class for an account in the database"""

    account_id = None
    host = None
    username = None
    info = None

    def __init__(self, acc: str, host: str, username: str, info: str) -> None:
        self.account_id = acc
        self.host = host
        self.username = username
        self.info = info

    def __str__(self) -> str:
        return json.dumps(
            {
                "id": str(self.
                          account_id) if self.account_id is not None else ' ',
                "host": self.host if self.host is not None else ' ',
                "username": str(self.
                                username) if self.username is not None else ' ',
                "info": str(self.info) if self.info is not None else ' '
            },
            indent=2
        )
