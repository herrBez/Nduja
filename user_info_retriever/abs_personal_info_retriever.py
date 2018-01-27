from abc import ABCMeta, abstractmethod


class PersonalInfoRetriever:
    __metaclass__ = ABCMeta

    @abstractmethod
    def retrieveInfo(self, username):
        pass
