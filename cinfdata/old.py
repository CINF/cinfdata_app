# -*- coding: utf-8 -*-
"""
Main file for the cinfdata app
"""


__version__ = '0.1'


from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.scatter import Scatter
from kivy.properties import StringProperty


class MainImage(Scatter):
    source = StringProperty(None)


class MainView(Widget):
    version = StringProperty(__version__)


class Cinfdata(Widget):
    pass

class CinfdataApp(App):
    def build(self):
        #root = self.root
        cinfdata = Cinfdata()
        # load the image
        #picture = MainImage(source='plot.png')
        # add to the main field
        #cinfdata.add_widget(picture)
        #print cinfdata.canvas.__dict__
        return cinfdata


if __name__ == '__main__':
    CinfdataApp().run()
