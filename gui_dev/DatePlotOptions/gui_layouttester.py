#!/usr/bin/env python

"""Runner of the gui layout development tool"""

import os
import argparse
from subprocess import call


WIDGETS = {
    'dateplotoptions',
}
DEVICES = {
    'phone': '-m screen:one,portrait,scale=0.30',
    'tablet': '',
}

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('widget', choices=WIDGETS, help='The widget to test')
parser.add_argument('--device', choices=DEVICES.keys(), default='phone',
                    help='The device to type to test on')

args = parser.parse_args()

os.environ['cinfdata_app_widget'] = args.widget

call('python main.py ' + DEVICES[args.device], shell=True)
