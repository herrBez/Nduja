from db.db_manager import DbManager
from user_info_retriever.bitbucket_info_retriever import BitbucketInfoRetriever
from user_info_retriever.github_info_retriever import GithubInfoRetriever
from user_info_retriever.twitter_info_retriever import TwitterInfoRetriever


class InfoRetriever:
    tokens = None

    def setTokens(tokens):
        try:
            GithubInfoRetriever.setToken(tokens['github'])
        except KeyError:
            pass
        try:
            TwitterInfoRetriever.setToken(tokens['twitter_app_key'],
                                          tokens['twitter_app_secret'],
                                          tokens['twitter_oauth_token'],
                                          tokens['twitter_oauth_token_secret'])
        except KeyError:
            pass

    def retrieveInfoForAccountSaved(self):
        db = DbManager.getInstance()
        accounts = db.getAllAccounts()
        for account in accounts:
            if account.info is None:
                info = None
                if "github" in account.host:
                    info = GithubInfoRetriever().retrieveInfo(
                        account.username)
                elif "bitbucket" in account.host:
                    info = \
                        BitbucketInfoRetriever().retrieveInfo(
                            account.username)
                elif "twitter" in account.host:
                    info = TwitterInfoRetriever().retrieveInfo(
                        account.username)
                if info is not None:
                    infoId = (db.insertInformation(info.name, info.website,
                                                   info.email, info.json))
                    db.addInfoToAccount(account.ID, infoId)
