"""Module for Dogecoin transaction retriever"""
from graph.chainso_transaction_retriever import ChainSoTransactionRetriever


class LtcTransactionRetriever(ChainSoTransactionRetriever):
    """subclass of chainso transaction retriever used for Litecoin"""
    def __init__(self):
        super().__init__("LTC")
