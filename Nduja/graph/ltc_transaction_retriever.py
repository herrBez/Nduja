from graph.chainso_transaction_retriever import ChainSoTransactionRetriever


class LtcTransactionRetriever(ChainSoTransactionRetriever):

    def __init__(self):
        super().__init__("LTC")
