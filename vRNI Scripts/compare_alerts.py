import csv
import json
 
vrops_alerts = open('vrops-network-alerts.csv', 'r', encoding='utf-8')
vrops_alerts_rdr = csv.reader(vrops_alerts)

vrni_alerts = open('vrni-network-alerts.csv', 'r', encoding='utf-8')
vrni_alerts_rdr = csv.reader(vrni_alerts) 

vrops_name_array = []
vrops_transfer_array = []
for vrops_row in vrops_alerts_rdr :
    vrops_name_array.append(vrops_row[1])
    vrops_transfer_array.append(vrops_row[0])

vrops_map = {}
for i in range(len(vrops_name_array)):
    if "vRNI" in vrops_name_array[i]:
        data = {
            vrops_name_array[i] : vrops_transfer_array[i]
        }
        vrops_map.update(data)


vrni_name_array = []
vrni_transfer_array = []
for vrni_row in vrni_alerts_rdr:
    vrni_name_array.append(vrni_row[1])
    vrni_transfer_array.append(vrni_row[0])

vrni_map = {}
for i in range(len(vrni_name_array)):
    #print(vrni_name)
    data = {
        vrni_name_array[i] : vrni_transfer_array[i]
    }
    vrni_map.update(data)


f = open('vrops_transfer.csv','w', newline='', encoding='utf-8-sig')
wr = csv.writer(f)

 
new_vrops_alerts = open('vrops-network-alerts.csv', 'r', encoding='utf-8')
new_vrops_alerts_rdr = csv.reader(new_vrops_alerts)

count = 0 


vrops_new_map = {}

for vrops_alert in vrops_map.keys():
    #print("### Chekc if this alert exists in vROPs ###")
    #print(vrops_alert)
    array = []
    for vrni_alert in vrni_map.keys():
        if vrni_alert in vrops_alert:
            count = count + 1
            data = {
                vrops_alert: vrni_map[vrni_alert]
            }
            vrops_new_map.update(data)
            #wr.writerow(array)
            break

print("Matched Alerts ---> " + str(len(vrops_new_map)))
        
i = 0
for vrops_row in new_vrops_alerts_rdr:
    print(vrops_row)
    array = []
    if vrops_row[1] in vrops_new_map.keys():
        array.append(vrops_new_map[vrops_row[1]])
        array.append(vrops_row[1])
        wr.writerow(array)
        i = i + 1
    else:
        array.append(vrops_row[0])
        array.append(vrops_row[1])
        wr.writerow(array)
        i = i + 1
            
print(str(i))
