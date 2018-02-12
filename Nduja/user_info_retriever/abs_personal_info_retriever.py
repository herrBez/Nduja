from abc import ABCMeta, abstractmethod
from typing import List
from dao.personal_info import PersonalInfo
from dao.account import Account


class PersonalInfoRetriever:
    """This class is the super class of all user info retriever and
    describes the interface for this type"""

    __metaclass__ = ABCMeta

    def retrieve_info(self, accounts: List[Account]) -> List[PersonalInfo]:
        """This method fetches the personal information of the given
        accounts. It follows the Template Method Pattern
        """
        result = []
        for account in accounts:
            result.append(self.retrieve_info_from_account(account))
        return result

    @abstractmethod
    def retrieve_info_from_account(self, account: Account) -> PersonalInfo:
        """This method fetches the information for a single Account
        and is specific for each subclass"""
        pass
