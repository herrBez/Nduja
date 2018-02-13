import json


class PersonalInfo:
    """DAO class for personal information"""

    name = ""
    website = ""
    email = ""
    json = ""

    def __init__(self, name: str, website: str, email: str,
                 json_string: str) -> None:
        self.name = name if name is not None else ' '
        self.website = website if website is not None else ' '
        self.email = email if email is not None else ' '
        self.json = json_string if json_string is not None else ' '

    def __str__(self) -> str:
        return json.dumps(
            {
                "name": self.name if self.name is not None else ' ',
                "website": self.website if self.website is not None else ' ',
                "email": self.email if self.email is not None else ' ',
                "json": self.json if self.json is not None else ' '
            },
            indent=2
        )

