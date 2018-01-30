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
        githubs = []
        bitbuckets = []
        twitters = []
        for account in accounts:
            if account.info is None:
                if "github" in account.host:
                    githubs.append(account)
                elif "bitbucket" in account.host:
                    bitbuckets.append(account)
                elif "twitter" in account.host:
                    twitters.append(account)
        infos = []
        infos = infos + GithubInfoRetriever().retrieveInfo(githubs)
        #(((infos.append(GithubInfoRetriever().retrieveInfo(githubs)))
        #  .append(BitbucketInfoRetriever().retrieveInfo(bitbuckets)))
        # .append(TwitterInfoRetriever().retrieveInfo(twitters)))
        accounts = []
        accounts = accounts + githubs
        #accounts = githubs.append(bitbuckets).append(twitters)
        accInfo = zip(accounts, infos)
        for (account, info) in accInfo:
            if info is not None:
                infoId = (db.insertInformation(info.name, info.website,
                                               info.email, info.json))
                db.addInfoToAccount(account.ID, infoId)
