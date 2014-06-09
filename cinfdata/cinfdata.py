"""Module that contains the cinfdata class"""

import StringIO
import urllib2
import base64
import json

from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.core.image.img_pygame import ImageLoaderPygame
from kivy.logger import Logger

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
        self.dateplot_options = {}

    def _get_data(self, url):
        request = urllib2.Request(url)
        request.add_header("Authorization", self.basestring)
        handle = urllib2.urlopen(request)
        data = handle.read()
        handle.close()
        return data

    def _get_json(self, url):
        return json.loads(self._get_data(url))

    def get_setups(self):
        """Get the list of setups from cinfdata"""
        url = '{}index_json.php'.format(self.url_start)
        return self._get_json(url)

    def get_plots(self, setup):
        """Get the plots from cinfdata for a specific setup"""
        url = '{}{}/info_json.php'.format(self.url_start, setup)
        return self._get_json(url)

    def update_datetime(self, name, value):
        self.dateplot_options[name] = value

    def form_plot_url(self):
        url = self.url_start + self.selected_plot.setup + '/plot.php?'
        options = {'type': self.selected_plot.plot,
                   'matplotlib': 'checked',
                   'image_format': 'png'}
        options['from'] = '{from_year:0>4}-{from_month:0>2}-{from_day:0>2}+'\
            '{from_hour:0>2}%3A{from_minute:0>2}'.format(**self.dateplot_options)
        options['to'] = '{to_year:0>4}-{to_month:0>2}-{to_day:0>2}+'\
            '{to_hour:0>2}%3A{to_minute:0>2}'.format(**self.dateplot_options)
        url += '&'.join(['='.join(kv) for kv in options.items()])
        url += '&left_plotlist[]=1&right_plotlist[]=2'  # HACK
        Logger.debug('cinfdata: url formed: ' + url)
        return url

    def get_plot(self):
        #addr = 'https://cinfdata.fysik.dtu.dk/thetaprobe/plot.php?type=multidateplot_pressures&from=2014-04-07+18:28&to=2014-04-08+18:29&left_ymax=0&left_ymin=0&right_ymax=0&right_ymin=0&left_logscale=checked&right_logscale=checked&matplotlib=checked&left_plotlist[]=1&right_plotlist[]=2&image_format=png'
        data = StringIO.StringIO(self._get_data(self.form_plot_url()))
        return ImageLoaderPygame(data)
        
