

# _id INTEGER PRIMARY KEY,
# Name VARCHAR(255),
# Website VARCHAR(255),
# Email VARCHAR(255),
# Json LONGTEXT
class PersonalInfo:
    ID = 0
    name = ""
    website = ""
    email = ""
    json = ""

    def __init__(self, ID, name, website, email, json):
        self.ID = ID
        self.name = name
        self.website = website
        self.email = email
        self.json = json
