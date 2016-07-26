

import json

import sys
print(sys.path)

from kivy.app import App
from kivy.uix.accordion import Accordion
from kivy.properties import ObjectProperty

__version__ = 0.1


class CinfdataApp(App):
    """This is the main CinfdataApp"""
    
    def build(self):
        with open('DatePlotOptions_input.json') as file_:
            setup_and_link = json.load(file_)
        return DatePlotOptions(setup_and_link)


class DatePlotOptions(Accordion):
    """Class for the date plot options"""

    cinfdata = ObjectProperty(None)

    def __init__(self, setup_and_link, **kwargs):
        import json
        with open('DatePlotOptions_input.json', 'w') as file_:
            json.dump(setup_and_link, file_)
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
            bl = BoxLayout(orientation='vertical', size_hint=(1, None))
            for dateplot, graph in natsorted(graphs.items(), key=itemgetter(0)):
                # Get a set of selected plots
                selected = {int(number) for number in
                            self.link['query_args'].get(plot_list, [])}

                # dateplot is something like: datelpot1
                btn = ToggleButton(text=graph['title'], size_hint_y=None, height=50)
                current_number = int(dateplot.replace('dateplot', ''))
                #btn.bind(on_release=partial(self.change_plotlist, plot_list, current_number))
                btn.bind(state=partial(self.change_plotlist, plot_list, current_number))
                bl.add_widget(btn)
                if current_number in selected:
                    btn.state = 'down'
            getattr(self.ids, plot_list).add_widget(bl)

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



def main():
    """Main run function"""
    app = CinfdataApp()
    app.run()


if __name__ == '__main__':
    main()
