# pylint: disable=no-name-in-module


"""Module that contains the main interface to the cinfdata.fysik.dtu.dk interface (The
Cinfdata class)

NOTE: The Cinfdata class is a kivy Widget. This was necessary in order to use the kivy
type properties (with observer pattern) for events.

"""

from io import BytesIO
import urllib2
import base64
import json
from pprint import pprint

from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.core.image import Image as CoreImage
from kivy.logger import Logger

class Cinfdata(Widget):
    """This class implements the main interface to the cinfdata.fysik.dtu.dk website

    Its primary function is to procvide convinience methods to get the data from the
    website

    """

    selected_plot = ObjectProperty(None)

    def __init__(self, gui, username, password):
        """Init urllib and data"""
        super(Cinfdata, self).__init__()

        self.gui = gui
        self.query_args = None
        self.dateplot_options = {}

        # Settings for urllib
        base64string = base64.encodestring(
            '{}:{}'.format(username, password)
            )[:-1]
        self.url_start = 'https://cinfdata.fysik.dtu.dk/'
        self.basestring = "Basic {}".format(base64string)

    def on_selected_plot(self, _, selected_plot):
        """Initialize GUI and query args"""
        setup, link = selected_plot
        query_args_in = link['query_args']
        self.query_args = {
            'left_plotlist': set(),
            'right_plotlist': set(),
        }

        self.gui.change_plot(selected_plot)
        Logger.debug('Cinfdata.on_selected_plot args after gui %s', self.query_args)

    def _get_data(self, url):
        """Return the bytes from a url"""
        Logger.debug('Cinfdata._get_data: %s', url)
        request = urllib2.Request(url)
        request.add_header("Authorization", self.basestring)
        handle = urllib2.urlopen(request)
        data = handle.read()
        handle.close()
        return data

    def _get_json(self, url):
        """Return the object decoded from json from url"""
        return json.loads(self._get_data(url))

    def get_setups(self):
        """Get the list of setups from cinfdata"""
        url = '{}data_as_json.php?request=index'.format(self.url_start)
        return self._get_json(url)

    def get_plots(self, setup):
        """Get the plots from cinfdata for a specific setup"""
        url = '{}{}/info_json.php'.format(self.url_start, setup)
        return self._get_json(url)

    def update_datetime(self, name, value):
        """Update a datetime value"""
        self.dateplot_options[name] = value

    def form_plot_url(self):
        """Returns formatted plot url"""
        _, link = self.selected_plot
        setup_folder = link['path'].lstrip('/').split('/')[0]
        url = self.url_start + setup_folder + '/plot.php?'
        options = {
            'type': link['query_args']['type'],
            'matplotlib': 'checked',
            'image_format': 'png'
        }

        # Add dateplot options FIXME check condition and move them into query args
        options['from'] = '{from_year:0>4}-{from_month:0>2}-{from_day:0>2}+'\
            '{from_hour:0>2}%3A{from_minute:0>2}'.format(**self.dateplot_options)
        options['to'] = '{to_year:0>4}-{to_month:0>2}-{to_day:0>2}+'\
            '{to_hour:0>2}%3A{to_minute:0>2}'.format(**self.dateplot_options)

        # Add boolean options
        for key in ('left_logscale', 'right_logscale'):
            if self.query_args.get(key, False):
                options[key] = 'checked'

        # Add everything from options
        url += '&'.join(['='.join(kv) for kv in options.items()])

        # Add lists to url
        for plotlist_name in ['left_plotlist', 'right_plotlist']:
            for plot_number in self.query_args[plotlist_name]:
                url += '&{}[]={}'.format(plotlist_name, plot_number)


        Logger.debug('cinfdata: url formed: ' + url)
        return url

    def get_plot(self):
        """Return a CoreImage from the current settings"""
        data = self._get_data(self.form_plot_url())
        return CoreImage(BytesIO(data), ext='png')
