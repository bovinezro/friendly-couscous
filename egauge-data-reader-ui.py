from pyforms.basewidget import BaseWidget
from pyforms.controls   import ControlFile
from pyforms.controls   import ControlText
from pyforms.controls   import ControlCombo
from pyforms.controls   import ControlButton
from datetime           import datetime
import time
import wget
import tempfile as tf
import xml.etree.ElementTree as ET


def generate_ts(d, m, y):
    ts = str(d) + "/" + str(m) + "/" + str(y)
    return int(time.mktime(datetime.strptime(ts, "%d/%m/%Y").timetuple()))

class EgaugeDataReader(BaseWidget):

    def __init__(self, *args, **kwargs):
        super().__init__('eGauge Date Reader')

        self._device_name = ControlText('Device Name', 'proto1')
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

        self._runbutton = ControlButton('Generate Report')
        self._runbutton.value = self.__buttonAction

        self._formset = [
            ('_device_name', '_output_file'),
            ('_start_date_day', '_start_date_month', '_start_date_year',
            '_end_date_day', '_end_date_month', '_end_date_year'),
            ('_runbutton'),
        ]

    def __buttonAction(self):
        startts = generate_ts(self._start_date_day.value, self._start_date_month.value, self._start_date_year.value)
        endts = generate_ts(self._end_date_day.value, self._end_date_month.value, self._end_date_year.value)
        device_name = self._device_name.value
        url = "http://" + device_name + ".egaug.es/cgi-bin/egauge-show?d&t=" + str(endts) + "&f=" + str(startts)

        temporary_output = tf.mkstemp()[1] + ".xml"
        xml_output = wget.download(url, temporary_output)

        tree = ET.parse(xml_output)
        root = tree.getroot()

        #get info from export
        export_info = root[0].attrib
        columns = export_info["columns"]
        timestamp = export_info["time_stamp"]
        timedelta = export_info["time_delta"]
        epoch = export_info["epoch"]

        #get list of register names
        reglist = []
        for i in range(0, int(columns) - 1):
            reglist.append(root[0][i].text)

        #get register name and all values for register
        def get_register_values(regname, columns):
            s = reglist.index(regname)
            columns = int(columns)
            n = [regname]
            while True:
                try:
                    test = root[0][int(columns)][s].text
                    test = str(test)
                except IndexError:
                    break
                else:
                    n.append(root[0][int(columns)][s].text)
                    columns +=1
            return(n)

        def get_cumulative_value(register_list):
            x = register_list[1]
            y = register_list[len(register_list) - 1]
            return (int(x) - int(y))
#stopping point
#test case
        s = 0
        while s < 5 :
            test1 = get_register_values(reglist[s], columns)
            test2 = get_cumulative_value(test1)
            print(test2)
            s += 1

if __name__ == '__main__':

    from pyforms import start_app
    start_app(EgaugeDataReader)
