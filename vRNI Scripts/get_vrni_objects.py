#!/usr/bin/python
# -*- coding: utf-8
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

def get_vrni_metrics(vrni_url, username, password, filename):

    base_url = base_url_tmp % vrni_url
    # Open CSV file for writing metrics
    f = open(filename + '.csv','w', newline='', encoding='utf-8-sig')
    wr = csv.writer(f)
    #  Login
    print("### Login into vRNI: " + vrni_url)

    data= {
        "username": "ykwak@vmware.com",
        "password": "Rhkrdudgns0105^",
        "tenantName": "field-demo.vrni.cmbu.local",
        "vIDMURL": "",
        "redirectURL": "",
        "authenticationDomains": {
            "0": {
                "domainType": "LDAP",
                "domain": "vmware.com",
                "redirectUrl": ""
            },
            "1": {
                "domainType": "LOCAL_DOMAIN",
                "domain": "localdomain",
                "redirectUrl": ""
            }
        },
        "currentDomain": 0,
        "domain": "vmware.com",
        "nDomains": 2,
        "serverTimestamp": "false",
        "loginFieldPlaceHolder": "Username"
    }

    

    resp = requests.post(
        base_url + '/api/auth/login',
        headers=headers, 
        json=data,
        verify=False)
    resp.raise_for_status()
    print(resp.headers['Set-Cookie'])
    
    print("----> Token " + json.dumps(resp.json()))
    headers['x-vrni-csrf-token'] =  "uiyhOZLFo/Gc97ZkJsz5yQ=="
    headers['Cookie'] =  "VRNI-JSESSIONID=6d4aedb2-4cf2-4b8a-a831-8efbf2027c28; vrniRoutingId=cGxhdGZvcm0y"
    



    print("### Logged into vRNI: " + vrni_url)

    print(headers)
    resp = requests.get(
        'https://field-demo.vrni.cmbu.local/api/model/objectTypes',
        headers=headers,
        verify=False)
    resp.raise_for_status()

    objectTypes = resp.json()['all']

    wr.writerow(["objectType", "displayName", "helpText", "isEventType", "isMetaType", "childTypes", "flags", "adminState", "eventSeverity"])

    for vrni_object in objectTypes:

        objectType = vrni_object['objectType']
        displayName = vrni_object['displayName']
        helpText = vrni_object['helpText']
        isEventType = vrni_object['isEventType']
        isMetaType = vrni_object['isMetaType']
        childTypes = vrni_object['childTypes']
        if "flags" in vrni_object:
            flags = vrni_object['flags']
        else: 
            flags = "none"
        adminState = vrni_object['adminState']
        eventSeverity = vrni_object['eventSeverity']

        array = []

        array.append(objectType)

        array.append(displayName)
        array.append(helpText)
        array.append(isEventType)
        array.append(isMetaType)
        array.append(childTypes)
        array.append(flags)
        array.append(adminState)
        array.append(eventSeverity)

        wr.writerow(array)

        print("#### done writing for " + vrni_object['displayName'])
  

 
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--hostname', default='field-demo.vrni.cmbu.local', help='vRealize Network Insight')
    parser.add_argument('-U', '--username', default='admin@local', help='vRealize Network Insight Admin Username')
    parser.add_argument('-P', '--password', default='VMware1!', help='Network Insight Admin Password')
    parser.add_argument('-F', '--filename', default='new-vrni-metrics', help='filename')

    args = parser.parse_args()

    get_vrni_metrics(args.hostname, args.username, args.password, args.filename)