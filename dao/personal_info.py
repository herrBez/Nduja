class PersonalInfo:
    name = ""
    website = ""
    email = ""
    json = ""

    def __init__(self, name, website, email, json):
        self.name = ' '
        self.website = ' '
        self.email = ' '
        self.json = ' '
        if self.name is not None:
            self.name = name
        if self.website is not None:
            self.website = website
        if self.email is not None:
            self.email = email
        if self.json is not None:
            self.json = json

    def __str__(self):
        namestr = ' '
        websitestr = ' '
        emailstr = ' '
        jsonstr = ' '
        if self.name is not None:
            namestr = self.name
        if self.website is not None:
            websitestr = self.website
        if self.email is not None:
            emailstr = self.email
        if self.json is not None:
            jsonstr = self.json
        return '{\n\t"name":"' + namestr + \
            '",\n\t"website":"' + websitestr + \
            '",\n\t"email":"' + emailstr + \
            '",\n\t"json":' + str(jsonstr) + \
            '}'
