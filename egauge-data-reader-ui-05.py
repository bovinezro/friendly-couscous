from pyforms.basewidget import BaseWidget
from pyforms.controls   import ControlFile
from pyforms.controls   import ControlText
from pyforms.controls   import ControlCombo
from pyforms.controls   import ControlButton
from pyforms.controls   import ControlEmptyWidget
from pyforms            import start_app
from datetime           import datetime
from fpdf               import FPDF
import matplotlib.pyplot as plt
import time
import wget
import tempfile as tf
import xml.etree.ElementTree as ET

reglist = []
root = []

def generate_ts(d, m, y):
    """generate a unix timestamp (required for eGauge API request) from numerical
    values provided for day, month, year"""
    ts = str(d) + "/" + str(m) + "/" + str(y)
    return int(time.mktime(datetime.strptime(ts, "%d/%m/%Y").timetuple()))

def get_register_values(regname, columns):
    """accepts a regname in the form reglist[x] and the number of
    columns in the export. Returns a list where the first item is the
    register name as a string and the following values are the
    cumulative values for that register"""
    global root
    s = reglist.index(regname)
    columns = int(columns)
    register_value_output = [regname]
    while True:
        try:
            test = root[0][int(columns)][s].text
            test = str(test)
        except IndexError:
            break
        else:
            register_value_output.append(root[0][int(columns)][s].text)
            columns +=1
    return(register_value_output)

def generate_report(register_value_output,
                   output_name,
                   start_day,
                   start_month,
                   start_year,
                   end_day,
                   end_month,
                   end_year):
    """Creates the actual report. Includes graph and text output. Saved as
    a PDF file. Accepts the starting and ending date values, a
    register_value_output (a list where the first item is the register name and
    additional items are the cumulative values for the register) and an output
    file name (generally assumed to the be the register name, but allowed to be
    different)"""
    #determine the cumulative value for entire period (start value - end value)
    x = register_value_output[1]
    y = register_value_output[len(register_value_output) - 1]
    cumulative = abs(int((int(x) - int(y)) / 3600000))
    #generate text output for report
    output_line_1 = ("The " +
                    str(register_value_output[0]) +
                    " register used " +
                    str(cumulative) +
                    " kWh."
                    )
    output_line_2 = ("Report period " +
                    str(start_month) +
                    "/" +
                    str(start_day) +
                    "/" +
                    str(start_year) +
                    " to " +
                    str(end_month) +
                    "/" +
                    str(end_day) +
                    "/" +
                    str(end_year)
                    )
    #get data for the graph
    #x_axis is number of days
    x_axis = []
    day_count = int(len(register_value_output)) - 2
    while day_count > 0:
        x_axis.insert(0, int(day_count))
        day_count = day_count - 1
    #y_axis is difference between cumulative values over each day
    y_axis = []
    s = 1
    for i in register_value_output:
        try:
            y_axis.insert(0, abs((int(register_value_output[s]) - int(register_value_output[s + 1])) / 3600000))
        except IndexError:
            break
        else:
            s += 1
    #plot the data, and save it as a temporary file in PNG format
    plt.plot(x_axis, y_axis)
    temp_image = tf.mkstemp()[1] + ".png"
    plt.savefig(temp_image)
    #create the PDF report
    pdf = FPDF('P', 'in', 'A4')
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(7, .4, txt=output_line_1, ln=1, align="C1")
    pdf.cell(7, .4, txt=output_line_2, ln=2, align="C1")
    pdf.image(temp_image, w = 7.25)
    pdf.output(output_name)

def month_day_gen(max_val, target):
    """generate entries in dropdown menu for the number of days and number of
    months"""
    tup = ()
    for i in range(1, max_val + 1):
        tup += (target.add_item(str(i), i),)
    return tup

def year_gen(min_val, target):
    """generate entries in the dropdown menus for number of years. Set to
    generate values from current year to the provided minimum value"""
    tup = ()
    for i in range (min_val, int("{:%Y}".format(datetime.now())) + 1):
        tup += (target.add_item(str(i), i),)
    return tup

class EgaugeReportGen(BaseWidget):
    """class containing all the pyforms stuff to make a nice UI."""
    def __init__(self, *args, **kwargs):
        super().__init__('eGauge Report Generator')
        #these are all user-editable fields
        self._device_name = ControlText('Device Name')
        self._start_date_day = ControlCombo('Starting Day')
        self._start_date_month = ControlCombo('Starting Month')
        self._start_date_year = ControlCombo('Starting Year')
        self._end_date_day = ControlCombo('Ending Day')
        self._end_date_month = ControlCombo('Ending Month')
        self._end_date_year = ControlCombo('Ending Year')
        self._register_list = ControlCombo('Select a register')
        #these functions automatically populate the day month and year fields
        #above with numerical values
        month_day_gen(31, self._start_date_day)
        month_day_gen(12, self._start_date_month)
        year_gen(2000, self._start_date_year)
        month_day_gen(31, self._end_date_day)
        month_day_gen(12, self._end_date_month)
        year_gen(2000, self._end_date_year)
        #these are thge buttons
        self._regButton = ControlButton('Fetch Registers')
        self._regButton.value = self.__regButtonAction
        self._runButton = ControlButton('Generate Report')
        self._runButton.value = self.__runButtonAction

        self._formset = [
            ('_device_name', '_regButton', '_register_list'),
            ('_start_date_day', '_start_date_month', '_start_date_year',
            '_end_date_day', '_end_date_month', '_end_date_year'),
            ('_runButton'),
            (''),
        ]

    def __regButtonAction(self):
        """button action for the Fetch Registers button. Gets a list of
        registers and poulates the register selection dropdown menu with them."""
        global root
        device_name = self._device_name.value
        url = "http://" + device_name + ".egaug.es/cgi-bin/egauge-show?n=1"
        temporary_output = tf.mkstemp()[1] + ".xml"
        xml_output = wget.download(url, temporary_output)
        tree = ET.parse(xml_output)
        root = tree.getroot()
        export_info = root[0].attrib
        columns = export_info["columns"]
        global reglist
        reglist = []
        for i in range(0, int(columns) - 1):
            reglist.append(root[0][i].text)
        tup = ()
        for i in reglist:
            tup += (self._register_list.add_item(str(i)),)
        return tup

    def __runButtonAction(self):
        """action to take place when using the "Run report" button. Generates
        a report containing the values for the selected register."""
        global root
        #generate starting timestamp, then set it back one day
        #required with the eGauge API to get the full date range
        startts = generate_ts(self._start_date_day,
                             self._start_date_month,
                             self._start_date_year
                             )
        startts = int(startts) - 86400
        #generate ending timestamp
        endts = generate_ts(self._end_date_day,
                           self._end_date_month,
                           self._end_date_year
                           )
        #set the device name
        device_name = self._device_name.value
        #create URL for CGI call to meter
        url = ("http://" +
              device_name +
              ".egaug.es/cgi-bin/egauge-show?h&t=" +
              str(startts) +
              "&f=" +
              str(endts)
              )
        #create a temporary file so wget can store the returned XML data
        temporary_output = tf.mkstemp()[1] + ".xml"
        #pull in the XML data from the temporary file
        xml_output = wget.download(url, temporary_output)
        #parse in the XML data using xml.etree.ElementTree
        tree = ET.parse(xml_output)
        root = tree.getroot()
        #get valuable info from export. not all of it is used, but it's trivial
        #to save it for future expansion
        export_info = root[0].attrib
        columns = export_info["columns"]
        timestamp = export_info["time_stamp"]
        timedelta = export_info["time_delta"]
        epoch = export_info["epoch"]
        #create an output file from the data for the selected register
        register = get_register_values(self._register_list.value, columns)
        output_file = self._register_list.value + ".pdf"
        output_file = output_file.replace("/", " ")
        generate_report(register,
                       output_file,
                       self._start_date_day,
                       self._start_date_month,
                       self._start_date_year,
                       self._end_date_day,
                       self._end_date_month,
                       self._end_date_year)

if __name__ == '__main__':
    start_app(EgaugeReportGen)
