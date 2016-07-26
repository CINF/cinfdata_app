
"""Layout tester for the cinfdata app"""

# 15m + 19:30-21:40

import os
import json
import sys
import argparse

from mock import MagicMock
from kivy.app import App
from kivy.uix.accordion import Accordion
from kivy.properties import ObjectProperty

import creds
from cinfdata import Cinfdata
from realmain import DatePlotOptions


class CinfdataApp(App):
    """This is the main CinfdataApp"""
    
    def build(self):
        widget = os.environ['cinfdata_app_widget']
        cinfdata = Cinfdata(self, creds.username, creds.password)
        if widget == 'dateplotoptions':
            with open('DatePlotOptions_input.json') as file_:
                setup, link = json.load(file_)
            main_widget = DatePlotOptions((setup, link))
            main_widget.cinfdata = MagicMock()
        
        return main_widget

def main():
    """Main run function"""
    app = CinfdataApp()
    app.run()


if __name__ == '__main__':
    main()
