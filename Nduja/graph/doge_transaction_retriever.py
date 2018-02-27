"""Module for Dogecoin transaction retriever"""
from graph.chainso_transaction_retriever import ChainSoTransactionRetriever


class DogeTransactionRetriever(ChainSoTransactionRetriever):
    """subclass of chainso transaction retriever used for Dogecoin"""
    def __init__(self):
        super().__init__("DOGE")
