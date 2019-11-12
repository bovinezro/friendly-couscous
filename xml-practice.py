import xml.etree.ElementTree as ET

tree = ET.parse('egauge-show.xml')
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


#testing
s = 0
while s < 5 :
    test1 = get_register_values(reglist[s], columns)
    test2 = get_cumulative_value(test1)
    print(test1)
    print(test2)
    s += 1

#register values are time based on second index, regname based on third index
regname = root[0][0].text
startval = root[0][11][0].text
endval = root[0][13][0].text

diff = int(startval) - int(endval)
#print(regname, str(diff))
