from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.carousel import Carousel
from kivy.uix.accordion import Accordion, AccordionItem

import creds
from interface import CinfdataInterface

class CinfdataApp(App):
    def build(self):
        return MainCarousel()


class MainCarousel(Carousel):
    pass


class PageSelection(Accordion):
    def __init__(self, **kwargs):
        super(PageSelection, self).__init__(**kwargs)
        cdi = CinfdataInterface(creds.username, creds.password)
        for setup in cdi.get_setups():
            item = AccordionItem(title=setup)
            for plot in cdi.get_dateplots(setup):
                item.add_widget(Label(text=plot))
            self.add_widget(item)



if __name__ == '__main__':
    app = CinfdataApp()
    app.run()
