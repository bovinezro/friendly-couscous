import xml.etree.ElementTree as ET

tree = ET.parse('egauge-show.xml')
root = tree.getroot()

#get info from export
export_info = root[0].attrib
columns = export_info["columns"]
timestamp = export_info["time_stamp"]
timedelta = export_info["time_delta"]
epoch = export_info["epoch"]

for i in range(0, int(columns) - 1):
    print(root[0][i].text)

for i in range(0, int(columns) - 1):
    print(root[0][int(columns)][i].text)    

regname = root[0][0].text
startval = root[0][11][0].text
endval = root[0][13][0].text

diff = int(startval) - int(endval)
print(regname, str(diff))

print(columns)
