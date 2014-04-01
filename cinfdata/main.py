
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.carousel import Carousel
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.config import Config
Config.set('kivy', 'log_level', 'debug')
from kivy.logger import Logger

import creds
from cinfdata import Cinfdata


def debug(obj):
    Logger.debug('#==>' + str(obj))


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
        self.cinfdata = Cinfdata(creds.username, creds.password)
        self.cinfdata.bind(selected_plot=self.change_plot)
        self.ids.page_selection.cinfdata = self.cinfdata
        # This emulates pressing the plot selection button and should set all
        # of the gui up for a specific plot
        self.cinfdata.selected_plot = self.ids.page_selection.first

    def on_index(self, *args):
        super(MainCarousel, self).on_index(*args)

    def change_plot(self, instance, value):
        pass#self.ids.lab1.text = value.plot

class PageSelection(Accordion):

    cinfdata = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(PageSelection, self).__init__(**kwargs)
        self.first = None

    def on_cinfdata(self, instance, value):

        # Dict that relates buttons to (setup, plot)
        self.plots = {}
        # Loop over the setups and create accordion item
        for setup in self.cinfdata.get_setups():
            item = AccordionItem(title=setup)
            box = BoxLayout(orientation='vertical')

            # Loop over plots for a setup and create PlotSelectButton (toggle)
            for plot in self.cinfdata.get_plots(setup):
                button = PlotSelectButton(setup, plot['type'],
                                          plot['graph_type'],
                                          text=plot['title'],
                                          on_press=self._select)
                self.plots[button] = (setup, plot)

                # Set first button as default #
                if self.first is None:
                    self.first = button
                    button.state = 'down'
                box.add_widget(button)

            box.add_widget(Label())
            item.add_widget(box)
            self.add_widget(item)

    def _select(self, *args):
        """Set the selected plot"""
        self.cinfdata.selected_plot = args[0]


class PlotSelectButton(ToggleButton):
    def __init__(self, setup, plot, plot_type, **kwargs):
        super(PlotSelectButton, self).__init__(**kwargs)
        self.setup = setup
        self.plot = plot
        self.plot_type = plot_type


class DatePlotOptions(Accordion):

    def __init__(self, **kwargs):
        super(DatePlotOptions, self).__init__(**kwargs)

    def change(self, instance, value):
        debug(str(instance) + ' changed to ' + str(value))

    def yikes(self, what):
        print 'jj'
        print self.ids.from_year.text

if __name__ == '__main__':
    app = CinfdataApp()
    app.run()
