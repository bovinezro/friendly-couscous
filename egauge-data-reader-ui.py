from pyforms.basewidget import BaseWidget
from pyforms.controls   import ControlFile
from pyforms.controls   import ControlText
from pyforms.controls   import ControlCombo
from pyforms.controls   import ControlButton
from datetime           import datetime
import wget
import tempfile
from urllib.request     import Request

class EgaugeDataReader(BaseWidget):

    def __init__(self, *args, **kwargs):
        super().__init__('eGauge Date Reader')

        self._device_name = ControlText('Device Name')
        self._output_file = ControlFile('Output File')
        self._start_date_day = ControlCombo('Starting Day')
        self._start_date_month = ControlCombo('Starting Month')
        self._start_date_year = ControlCombo('Starting Year')
        self._end_date_day = ControlCombo('Ending Day')
        self._end_date_month = ControlCombo('Ending Month')
        self._end_date_year = ControlCombo('Ending Year')
        self._granularity = ControlCombo('Data Granularity')
        self._granularity.add_item('Day', 'd')
        self._granularity.add_item('Hour', 'h')
        self._granularity.add_item('Minute', 'm')

        def month_day_gen(max_val, target):
            tup = ()
            for i in range(1, max_val + 1):
                tup += (target.add_item(str(i), i),)
            return tup

        def year_gen(min_val, target):
            tup = ()
            for i in range (min_val, int("{:%Y}".format(datetime.now())) + 1):
                tup += (target.add_item(str(i), i),)
            return tup

        month_day_gen(31, self._start_date_day)
        month_day_gen(12, self._start_date_month)
        year_gen(2000, self._start_date_year)
        month_day_gen(31, self._end_date_day)
        month_day_gen(12, self._end_date_month)
        year_gen(2000, self._end_date_year)

        self._formset = [
            ('_device_name', '_output_file'),
            ('_start_date_day', '_start_date_month', '_start_date_year',
            '_end_date_day', '_end_date_month', '_end_date_year'),
            ('_granularity'),
        ]


    def generate_url(start_ts, end_ts, gran_variable, device_name):
        #read_url =
        #something
        return read_url

    def request_data(url):
        wget.download(read_url, tf.mkstemp())
        #something
        return data

    def generate_report(data):
        something
        return file

if __name__ == '__main__':

    from pyforms import start_app
    start_app(EgaugeDataReader)
