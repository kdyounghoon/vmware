#!/usr/bin/python
# -*- coding: utf-8

##########################################################
# Get vROPS NSX-T Alerts 
##########################################################
# By Younghoon, May 2021
##########################################################

import requests
import json
import csv
import argparse
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

base_url_tmp = 'https://%s'
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

def get_nsx_alerts(nsx_url, username, password, filename):

    base_url = base_url_tmp % nsx_url
    # Open CSV file for writing alerts
    f = open(filename + '.csv','w', newline='', encoding='utf-8-sig')
    wr = csv.writer(f)
    #  Login
    print("### Login into NSX: " + nsx_url)

    headers['Authorization'] = "Basic YWRtaW46ZGVtb1ZNd2FyZTEh"

    # Get Alerts
    resp = requests.get(
        base_url + '/api/v1/events',
        headers=headers,
        verify=False)
    resp.raise_for_status()
    alerts = resp.json()['results']


    wr.writerow([
        "event_type_display_name", 
        "node_types", 
        "summary", 
        "description",
        "recommended_action", 
        "severity", 
        "event_true_snmp_oid", 
        "event_false_snmp_oid",
        "is_threshold_fixed",
        "is_disabled",
        "threshold",
        "sensitivity",
        "suppress_alarm",
        "suppress_snmp_trap",
        "entity_resource_type",
        "ClusterNodeConfig",
    ])
    number_of_alerts = 0
    for alert in alerts:
        # Alert
        array = []

        array.append(alert['event_type_display_name'])
        
        array.append(alert['node_types'])

        array.append(alert['summary'])

        array.append(alert['description'])

        array.append(alert['recommended_action'])

        array.append(alert['severity'])

        array.append(alert['event_true_snmp_oid'])

        array.append(alert['event_false_snmp_oid'])

        array.append(alert['is_threshold_fixed'])
   
        array.append(alert['is_disabled'])
     
        array.append(alert['threshold'])
 
        array.append(alert['sensitivity'])

        array.append(alert['suppress_alarm'])

        array.append(alert['suppress_snmp_trap'])

        array.append(alert['entity_resource_type'])


        wr.writerow(array)
        number_of_alerts += 1
    
    
    print("### The number of alerts written " + str(number_of_alerts))
    print("### Filename is  " + filename)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--hostname', default='nsxmgr-01a.corp.local', help='NSX-T')
    parser.add_argument('-U', '--username', default='admin', help='NSX-T Admin Username')
    parser.add_argument('-P', '--password', default='VMware1!', help='NSX-T Admin Password')
    parser.add_argument('-F', '--filename', default='NSX-alerts', help='filename')

    args = parser.parse_args()

    get_nsx_alerts(args.hostname, args.username, args.password, args.filename)