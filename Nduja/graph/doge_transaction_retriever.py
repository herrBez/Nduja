from graph.chainso_transaction_retriever import ChainSoTransactionRetriever


class DogeTransactionRetriever(ChainSoTransactionRetriever):

    def __init__(self):
        super().__init__("DOGE")
