import urllib2
import base64
import json

class CinfdataInterface(object):
    base = 'https://cinfdata.fysik.dtu.dk/'

    def __init__(self, username, password):
        base64string = base64.encodestring(
            '{}:{}'.format(username, password)
            )[:-1]
        self.basestring = "Basic {}".format(base64string)

    def _get_data(self, url):
        request = urllib2.Request(url)
        request.add_header("Authorization", self.basestring)
        handle = urllib2.urlopen(request)
        content = json.loads(handle.read())
        handle.close()
        return content

    def get_setups(self):
        url = '{}index_json.php'.format(self.base)
        return self._get_data(url)

    def get_dateplots(self, setup):
        url = '{}{}/info_json.php'.format(self.base, setup)
        return self._get_data(url)
