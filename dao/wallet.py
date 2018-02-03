class Wallet:
    address = None
    currency = None
    status = None
    file = None

    def __init__(self, add, curr, f, u):
        self.address = add
        self.currency = curr
        self.file = f
        self.status = u

    def __str__(self):
        address_str = ''
        currency_str = ''
        status_str = ''
        if self.address is not None:
            address_str = str(self.address)
        if self.currency is not None:
            currency_str = str(self.currency)
        if self.status is not None:
            status_str = str(self.status)
        return ('{\n    "address":"' + address_str + '",\n    "currency":"' +
                currency_str + '",\n    "status":"' + status_str + '"\n}')
