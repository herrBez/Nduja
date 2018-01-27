class Account:
    ID = None
    host = None
    username = None
    info = None

    def __init__(self, ID, host, username, info):
        self.ID = ID
        self.host = host
        self.username = username
        self.info = info

    def __str__(self):
        idstr = ' '
        hoststr = ' '
        usernamestr = ' '
        infostr = ' '
        if self.ID is not None:
            idstr = str(self.ID)
        if self.host is not None:
            hoststr = str(self.host)
        if self.username is not None:
            usernamestr = str(self.username)
        if self.info is not None:
            infostr = str(self.info)
        return '{\n\t"id":"' + idstr + \
            '",\n\t"host":"' + hoststr + \
            '",\n\t"username":"' + usernamestr + \
            '",\n\t"info":"' + infostr + \
            '"\n}'
