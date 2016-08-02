# pylint: disable=no-name-in-module,no-member
"""Main file for the Cinfdata app.

This file contains mainly the UI. The file cinfdata.py contains the core interface to the
data from cinfdata.fysik.dtu.dk.

The Main UI is laid out like a carousel with 3 pages:

+----------+--------+-----------+
| Plot     | Main   | Page      |
| Settings | Figure | Selection |
+----------+--------+-----------+

DESCRIBE PLOT SETTINGS

The main figure page is the page in which the figure is displayed. It is layed out main in
kivy language. It is a FloatLayout with a pinch zoom and pointer movable figure
(MainImage, id=main_image). MainImage is defined both in kivy lang and in this file.

The page selection page is the page in which the setup and plot page is selected. It is
layed out in the PageSelection class (both in kivy lang and in this file). The main
components are a DropDown to select the setup and below that a BoxLayout with pages in a
ScrollView.

"""

from __future__ import print_function

import time
import calendar
from pprint import pprint
from functools import partial
from operator import itemgetter

from natsort import natsorted

from kivy.app import App
from kivy.uix.accordion import Accordion
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.carousel import Carousel
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scatter import Scatter
from kivy.uix.scrollview import ScrollView
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.popup import Popup
from kivy.core.image import Image as CoreImage
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.config import Config
Config.set('kivy', 'log_level', 'debug')
from kivy.logger import Logger

try:
    import creds
except ImportError:
    creds = None
from cinfdata import Cinfdata

__version__ = '0.1'

class CinfdataApp(App):
    """This is the main CinfdataApp"""
    def build(self):
        return MainCarousel()

    def on_pause(self):
        return True

class MainCarousel(Carousel):
    """Main cinfdata class.

    Contains the current settings and provides an interface to the cinfdata
    information
    """
    def __init__(self, **kwargs):
        super(MainCarousel, self).__init__(**kwargs)

        self.waiting_png = CoreImage('data/waiting.png')

        Clock.schedule_once(self._after_init)

    def _after_init(self, _):
        """Get password"""
        username = password = None
        if creds is not None:
            username, password = creds.username, creds.password

        # Implement using password managers
        if username is None:
            # username, password = password.get_creds()
            pass

        # If we git creds from creds module or password managers, set callback
        if username is not None:
            callback = partial(self._after_password, username, password)
            Clock.schedule_once(callback)
            return

        # Otherwise, ask for them (PasswordOpen will call _after_password)
        pw = PasswordPopup(self)
        pw.open()

    def _after_password(self, username, password, _):
        """After password has been received, initialize cinfdata"""
        # Initiate cinfdata and bind properties
        self.cinfdata = Cinfdata(self, username, password)

        # FIXME, check password somehow and think about how to come
        # back to _after_init

        # Add a reference to cinfdata to page selection
        self.ids.page_selection.cinfdata = self.cinfdata
        self.ids.main_image.cinfdata = self.cinfdata

    def on_index(self, *args):
        """Update image when switcing into the middle carousel part

        on_index is called the caroudel is turned into a new position
        """
        super(MainCarousel, self).on_index(*args)
        Logger.debug('MainCarousel: index: {}'.format(args[1]))
        if args[1] == 1:
            # First time on_index is called, there is no cinfdata object yet
            if not hasattr(self, 'cinfdata'):
                print("no cindata yet")
                return

            # Also we switch back to 
            if self.cinfdata.selected_plot is None:
                return
            self.ids.main_image.update_image(self.waiting_png)
            Clock.schedule_once(self._get_image_and_update)

    def _get_image_and_update(self, _):
        """Get image from cinfdata and update main image"""
        data = self.cinfdata.get_plot()
        self.ids.main_image.update_image(data)

    def change_plot(self, setup_and_link):
        """Change the plot settings widget when a new plot is selected"""
        #Logger.debug("Change plot %s", setup_and_link[0])
        #Logger.debug("Change plot %s", setup_and_link[1])
        _, link = setup_and_link
        if link['pagetype'] == 'dateplot':
            self.ids.plot_settings.clear_widgets()
            dateplot_options = DatePlotOptions(setup_and_link)
            dateplot_options.cinfdata = self.cinfdata
            self.ids.plot_settings.add_widget(dateplot_options)
        else:
            message = 'Support for the \'{}\' plot type is not yet implemented'\
                .format(link['pagetype'])
            raise NotImplementedError(message)


class SetupButton(Button):
    """Class used for a setup button

    It stores information about the setup in the data property

    """
    def __init__(self, *args, **kwargs):
        self.data = kwargs.pop('setup')
        super(SetupButton, self).__init__(*args, **kwargs)


class PageSelection(BoxLayout):
    """The "right" widget, that is used to select which page to plot"""

    cinfdata = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(PageSelection, self).__init__(**kwargs)
        self.mainbutton = Button(text='Select Setup', size_hint=(1, 0.2))
        self.pages_widget = BoxLayout(orientation='vertical', size_hint=(1, None))
        #self.pages_widget.bind(minimum_height=self.pages_widget.setter('height'))
        self.pages_widget.add_widget(Button(text='Pages', size_hint=(1, 1)))
        self.scroll_view = ScrollView(size_hint=(1, 0.8), do_scroll_x=False)
        self.scroll_view.add_widget(self.pages_widget)
        self.add_widget(self.mainbutton)
        self.add_widget(self.scroll_view)

    def on_cinfdata(self, instance, value):
        """Setup the setup selection page, when the cinfdata ObjectProperty is set
        (happens only on startup)"""

        dropdown = DropDown()

        for setup in self.cinfdata.get_setups():
            # Do not show setups that has no dateplots
            if len([l for l in setup['links']
                    if l['pagetype'] == 'dateplot']) == 0:
                continue
            btn = SetupButton(text='Setup: ' + setup['title'], size_hint_y=None,
                              height=44, setup=setup)
            btn.bind(on_release=lambda btn: dropdown.select(btn))
            dropdown.add_widget(btn)

        self.mainbutton.bind(on_release=lambda widget: dropdown.open(widget))
        dropdown.bind(on_select=self._select)

    def _select(self, dropdown, setup_button):
        """Set the selected plot"""
        Logger.debug('PageSelection._select: %s', setup_button.text)
        self.mainbutton.text = setup_button.text

        self.pages_widget.clear_widgets()
        setup = setup_button.data
        for link in setup_button.data['links']:
            # So far only dateplots are implemented
            if link['pagetype'] != 'dateplot':
                continue
            codename = setup['codename']
            button = ToggleButton(text=link['title'], group=codename,
                                  size_hint_y=None, height=50)
            button.bind(on_release=partial(self._select_page, setup, link))
            self.pages_widget.add_widget(button)
        self.pages_widget.height = len(setup_button.data['links']) * 50
        # Eventually set self.cinfdata.selected_plot with (setup, link)

    def _select_page(self, setup, link, widget):
        """  """
        Logger.debug('PageSelection._select_page: %s - %s', setup['title'], link['title'])
        self.cinfdata.selected_plot = (setup, link)


class DatePlotOptions(Accordion):
    """Class for the date plot options"""

    cinfdata = ObjectProperty(None)

    def __init__(self, setup_and_link, **kwargs):
        #import json
        #with open('DatePlotOptions_input.json', 'w') as file_:
        #    json.dump(setup_and_link, file_)
        super(DatePlotOptions, self).__init__(**kwargs)
        self.setup, self.link = setup_and_link
        self.intervals = ['year', 'month', 'day', 'hour', 'minute']

    def on_cinfdata(self, instance, value):
        """Update the values in cinfdata from the values in the controls when
        the cinfdata ObjectProperty is set (this happens only on when
        this class if first instantiated)

        """
        # Set up log scale widgets
        query_args_in = self.link['query_args']
        for side in ('left', 'right'):
            state_str = query_args_in.get(side + '_logscale', '')
            if state_str == 'checked':
                getattr(self.ids, side + '_log').state = 'down'

        # Form left and right selection boxes
        graphs = {key: value for key, value in self.link['graphsettings'].items()
                 if key.startswith('dateplot')}
        for plot_list in ['left_plotlist', 'right_plotlist']:
            plot_list_widget = getattr(self.ids, plot_list)
            #bl = BoxLayout(orientation='vertical', size_hint=(1, 1))
            for dateplot, graph in natsorted(graphs.items(), key=itemgetter(0)):
                # Get a set of selected plots
                selected = {int(number) for number in
                            self.link['query_args'].get(plot_list, [])}

                # dateplot is something like: datelpot1
                btn = ToggleButton(text=graph['title'], size_hint=(1, 1))
                current_number = int(dateplot.replace('dateplot', ''))
                #btn.bind(on_release=partial(self.change_plotlist, plot_list, current_number))
                btn.bind(state=partial(self.change_plotlist, plot_list, current_number))
                plot_list_widget.add_widget(btn)
                #bl.add_widget(btn)
                if current_number in selected:
                    btn.state = 'down'
            #getattr(self.ids, plot_list).add_widget(bl)

        # write the values from the controls into cinfdata
        for direction in ['from', 'to']:
            for interval in self.intervals:
                name = '{}_{}'.format(direction, interval)
                self.cinfdata.update_datetime(
                    name, self.gui(direction, interval).text
                    )
        self.cinfdata.update_datetime('to_active', self.gui('to', 'active').active)


    def gui(self, direction, interval):
        """Convinience to get widget direction_interval e.g. from_hour"""
        return getattr(self.ids, '{}_{}'.format(direction, interval))

    def change(self, instance, value):
        """Date time widgets have changes values, update accordingly"""
        Logger.debug('DatePlotOptions:change')
        self.cinfdata.update_datetime(instance.name, value)
        # name is e.g. 'from_day'
        direction, interval = instance.name.split('_')
        # If we update the month or year, we must also update the day control
        # with appropriate values
        if interval in ['month', 'year']:
            year = int(self.gui(direction, 'year').text)
            month = int(self.gui(direction, 'month').text)
            day_spinner = self.gui(direction, 'day')
            month_range = calendar.monthrange(year, month)[1]
            # Coerce in range
            new_selected_day = min(max(1, int(day_spinner.text)), month_range)
            day_spinner.text = str(new_selected_day)
            day_spinner.values = [str(d) for d in range(month_range, 0, -1)]
            self.cinfdata.update_datetime('{}_day'.format(direction),
                                          new_selected_day)

    def change_plotlist(self, plot_list, dateplot_number, _, state):
        Logger.debug('change_plotlist(%s, %s, %s)', plot_list, dateplot_number, state)
        if state == 'down':
            self.cinfdata.query_args[plot_list].add(dateplot_number)
        else:
            self.cinfdata.query_args[plot_list].remove(dateplot_number)

    def set_ago(self, interval):
        """Set time to now minus interval"""
        Logger.debug('DatePlotOptions:set_ago ' + str(interval))
        times = {
            'from': time.strftime('%Y_%m_%d_%H_%M',
                                  time.localtime(time.time() - interval)).split('_')
            }
        times['to'] = time.strftime('%Y_%m_%d_%H_%M').split('_')
        for direction in ['from', 'to']:
            for interval, value in zip(self.intervals, times[direction]):
                self.gui(direction, interval).text = value.lstrip('0')

    def set_to_state(self, state):
        """Enable or disable the to controls"""
        Logger.debug('DatePlotOptions:set_to_state ' + str(state))
        self.cinfdata.update_datetime('to_active', state)

    def set_log(self, side, state):
        """Callback for log scale buttons"""
        Logger.debug('DatePlotOptions.set_log(%s, %s)', side, state)
        self.cinfdata.query_args[side + '_logscale'] = state

class NoNetworkError(Popup):
    """Custom no network error popup"""


class MainImage(Scatter):
    """Class for the main image"""

    cinfdata = None

    def __init__(self, **args):
        super(MainImage, self).__init__(**args)
        self.first = True

    def update_image(self, data):
        """Update the image"""
        with self.ids.image.canvas:
            self.ids.image.texture = data.texture
        self.ids.image.canvas.ask_update()


class PasswordPopup(Popup):
    """A password for credentials"""

    def __init__(self, main, *args, **kwargs):
        super(PasswordPopup, self).__init__(*args, **kwargs)
        self.main = main

    def dismiss(self, *args, **kwargs):
        """Override dismiss action"""
        callback = partial(
            self.main._after_password,
            self.ids.username.text,
            self.ids.password.text,
        )
        Clock.schedule_once(callback)
        super(PasswordPopup, self).dismiss(*args, **kwargs)

def main():
    """Main run function"""
    app = CinfdataApp()
    app.run()


if __name__ == '__main__':
    main()
