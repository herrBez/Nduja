from abc import ABCMeta, abstractmethod
import json
import requests

class AbsWalletCollector:
    '''Abstract base class for the Address Collector'''
    __metaclass__ = ABCMeta
        
    @abstractmethod
    def collect_address(self):
        '''Abstract method that must be returns a json '''
    
    
    def request_url(self, url, token = None):
        """ Request an url synchronously and returns the json response"""
        data = None
        if not token is None:
            data = {'Authorization': 'token ' + token}
        r = requests.get(url, headers=data)
        resp = r.text
        # ~ json.loads(resp) # if it is not well formatted exit
        return resp

pass
