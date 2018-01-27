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
