
import time
import calendar
import StringIO
from functools import partial

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.carousel import Carousel
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.scatter import Scatter
from kivy.core.image import Image as CoreImage
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.config import Config
Config.set('kivy', 'log_level', 'debug')
from kivy.logger import Logger

import creds
from cinfdata import Cinfdata

__version__ = 0.1

class CinfdataApp(App):
    def build(self):
        return MainCarousel()

class MainCarousel(Carousel):
    """Main cinfdata class.

    Contains the current settings and provides an interface to the cinfdata
    information
    """
    def __init__(self, **kwargs):
        super(MainCarousel, self).__init__(**kwargs)
        # Initiate cinfdata and bind properties
        self.cinfdata = Cinfdata(creds.username, creds.password)
        self.cinfdata.bind(selected_plot=self.change_plot)

        # Add a reference to cinfdata to page selection
        self.ids.page_selection.cinfdata = self.cinfdata
        self.ids.main_image.cinfdata = self.cinfdata

        # Initiate date plot options and add cinfdata reference
        self.dateplot_options = DatePlotOptions()
        self.dateplot_options.cinfdata = self.cinfdata

        self.waiting_png = CoreImage('data/waiting.png')

    def on_index(self, *args):
        """Update image when switcing into the middle carousel part

        on_index is called the caroudel is turned into a new position
        """
        super(MainCarousel, self).on_index(*args)
        Logger.debug('MainCarousel: index: {}'.format(args[1]))
        if args[1] == 1:
            # First time on_index is called, there is no cinfdata object yet
            if not hasattr(self, 'cinfdata'):
                return
            self.ids.main_image.update_image(self.waiting_png)
            Clock.schedule_once(self._get_image_and_update)
    
    def _get_image_and_update(self, time):
        """Get image from cinfdata and update main image"""
        data = self.cinfdata.get_plot()
        self.ids.main_image.update_image(data)

    def change_plot(self, obj, setup_and_link):
        """Change the plot settings widget when a new plot is selected"""
        setup, link = setup_and_link
        #index = self.index
        if link['pagetype'] == 'dateplot':
            self.ids.plot_settings.clear_widgets()
            self.ids.plot_settings.add_widget(self.dateplot_options)
            #self.remove_widget(self.slides[0])
            #self.add_widget(self.dateplot_options, -2)
            #self.index = index
        else:
            message = 'Support for the \'{}\' plot type is not yet implemented'.format(link['pagetype'])
            raise(NotImplementedError(message))


class PageSelection(Accordion):

    cinfdata = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(PageSelection, self).__init__(**kwargs)

    def on_cinfdata(self, instance, value):
        Logger.debug('PageSelection on_cinfdata')
        for setup in self.cinfdata.get_setups():
            item = AccordionItem(title=setup['title'])
            box = BoxLayout(orientation='vertical')

            # Loop over plots for a setup and create PlotSelectButton (toggle)
            for link in setup['links']:
                callback = partial(self._select, setup, link)
                button = ToggleButton(text=link['title'], on_press=callback)
                box.add_widget(button)

            box.add_widget(Label())
            item.add_widget(box)
            self.add_widget(item)
            break

    def _select(self, setup, link, widget):
        """Set the selected plot"""
        Logger.debug('PageSelection._select: "%s", "%s" %s', setup['title'],
                     link['pagetype'], widget)
        self.cinfdata.selected_plot = (setup, link)


class PlotSelectButton(ToggleButton):
    def __init__(self, setup, plot, plot_type, **kwargs):
        super(PlotSelectButton, self).__init__(**kwargs)
        self.setup = setup
        self.plot = plot
        self.plot_type = plot_type


class DatePlotOptions(Accordion):

    cinfdata = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(DatePlotOptions, self).__init__(**kwargs)
        self.intervals = ['year', 'month', 'day', 'hour', 'minute']                    

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

    def on_cinfdata(self, instance, value):
        # write the values from the controls into cinfdata
        for direction in ['from', 'to']:
            for interval in self.intervals:
                name = '{}_{}'.format(direction, interval)
                self.cinfdata.update_datetime(
                    name, self.gui(direction, interval).text
                    )
        self.cinfdata.update_datetime('to_active', self.gui('to', 'active').active)

    def set_ago(self, interval):
        """Set time to now minus interval"""
        Logger.debug('DatePlotOptions:set_ago ' + str(interval))
        times = {
            'from': time.strftime('%Y_%m_%d_%H_%M',
                                  time.localtime(time.time() - interval)
                                  ).split('_')
            }
        times['to'] = time.strftime('%Y_%m_%d_%H_%M').split('_')
        for direction in ['from', 'to']:
            for interval, value in zip(self.intervals, times[direction]):
                self.gui(direction, interval).text = value.lstrip('0')

    def set_to_state(self, state):
        """Enable or disable the to controls"""
        Logger.debug('DatePlotOptions:set_to_state ' + str(state))
        self.cinfdata.update_datetime('to_active', state)
        nn = NoNetworkError()
        nn.open()


class NoNetworkError(Popup):
    pass


class MainImage(Scatter):

    cinfdata = None

    def __init__(self, **args):
        super(MainImage, self).__init__(**args)
        self.first = True

    def update_image(self, data):
        """Update the image"""
        with self.ids.image.canvas:
            self.ids.image.texture = data.texture
        self.ids.image.canvas.ask_update()
            

if __name__ == '__main__':
    app = CinfdataApp()
    app.run()
