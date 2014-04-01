"""Module that contains the cinfdata class"""

import urllib2
import base64
import json

from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty

class Cinfdata(Widget):

    selected_plot = ObjectProperty(None)

    def __init__(self, username, password):
        """Init urllib and data"""
        # Settings for urllib
        base64string = base64.encodestring(
            '{}:{}'.format(username, password)
            )[:-1]
        self.url_start = 'https://cinfdata.fysik.dtu.dk/'
        self.basestring = "Basic {}".format(base64string)

    def _get_data(self, url):
        request = urllib2.Request(url)
        request.add_header("Authorization", self.basestring)
        handle = urllib2.urlopen(request)
        content = json.loads(handle.read())
        handle.close()
        return content

    def get_setups(self):
        """Get the list of setups from cinfdata"""
        return ['setup1', 'setup2']
        #url = '{}index_json.php'.format(self.url_start)
        #return self._get_data(url)

    def get_plots(self, setup):
        """Get the plots from cinfdata for a specific setup"""
        return [{'type': 'type1', 'graph_type': 'date', 'title': 'MyTitle'}] * 2
        #url = '{}{}/info_json.php'.format(self.url_start, setup)
        #return self._get_data(url)
