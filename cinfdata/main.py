from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.carousel import Carousel
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.boxlayout import BoxLayout

import creds
from interface import CinfdataInterface

CDI = CinfdataInterface(creds.username, creds.password)

class CinfdataApp(App):
    def build(self):
        return MainCarousel()

class MainCarousel(Carousel):
    def __init__(self, **kwargs):
        super(MainCarousel, self).__init__(**kwargs)
    def on_index(self, *args):
        super(MainCarousel, self).on_index(*args)
        print args[0].index


class PageSelection(Accordion):
    def __init__(self, **kwargs):
        super(PageSelection, self).__init__(**kwargs)

        self.plots = {}
        self.selected = None
        for setup in CDI.get_setups():
            print setup
            item = AccordionItem(title=setup)
            box = BoxLayout(orientation='vertical')
            for plot in CDI.get_dateplots(setup):
                button = PlotSelectButton(text=plot, on_press=self._select)
                self.plots[button] = (setup, plot)
                if self.selected is None:
                    button.state = 'down'
                    self.selected = (setup, plot)
                box.add_widget(button)
            box.add_widget(Label())
            item.add_widget(box)
            self.add_widget(item)

    def _select(self, *args):
        self.selected = args[0]

class PlotSelectButton(ToggleButton):
    def __init__(self, **kwargs):
        super(PlotSelectButton, self).__init__(**kwargs)

if __name__ == '__main__':
    app = CinfdataApp()
    app.run()
