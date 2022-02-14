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
 
    headers['x-vrni-csrf-token'] =  "zwF+7YS7YeD7ohj0+I07pw=="
    headers['Cookie'] =  "VRNI-JSESSIONID=4252e33e-6c76-46d9-bcd2-baabbe4effcb; vrniRoutingId=cGxhdGZvcm0z"
    



    print("### Logged into vRNI: " + vrni_url)

    print(headers)
    resp = requests.get(
        'https://field-demo.vrni.cmbu.local/api/model/objectTypes',
        headers=headers,
        verify=False)
    resp.raise_for_status()

    objectTypes = resp.json()['all']

    wr.writerow(["object", "metric/denorm", "propertyType", "canonicalName", "friendlyName", "aliases", "helpText"])

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

   
        if isEventType is False and isMetaType is False:
                resp = requests.get(
                    'https://field-demo.vrni.cmbu.local/api/model/properties?objectType=' + str(objectType),
                    headers=headers,
                    verify=False)
                resp.raise_for_status()

                metrics = resp.json()[str(objectType)]['_metric']
                
                if "_denorm" in resp.json()[str(objectType)]:
                    denorms = resp.json()[str(objectType)]['_denorm']

                for metric in metrics.keys():

                    array = []
                    array.append(displayName)
                    array.append("metric")
                    array.append(metrics[metric]['propertyType'])
                    array.append(metrics[metric]['canonicalName'])
                    array.append(metrics[metric]['friendlyName'])    
             
                    if "aliases" in metrics[metric]:
                        array.append(metrics[metric]['aliases'])    
                    if "helpText" in metrics[metric]:
                        array.append(metrics[metric]['helpText'])   
                    
                    wr.writerow(array)
                    print("#### done writing for " + displayName + " : " + metrics[metric]['friendlyName'])
            
                for denorm in denorms:

                    array = []
                    array.append(displayName)
                    array.append("denorm")
                    array.append(denorms[denorm]['propertyType'])
                    array.append(denorms[denorm]['canonicalName'])
                    array.append(denorms[denorm]['friendlyName'])

                    if "aliases" in denorms[denorm]:
                        array.append(denorms[denorm]['aliases'])
                    if "helpText" in denorms[denorm]:
                        array.append(denorms[denorm]['helpText'])

                    wr.writerow(array)
                    print("#### done writing for " + displayName + " : " + denorms[denorm]['friendlyName'])


 
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--hostname', default='field-demo.vrni.cmbu.local', help='vRealize Network Insight')
    parser.add_argument('-U', '--username', default='admin@local', help='vRealize Network Insight Admin Username')
    parser.add_argument('-P', '--password', default='VMware1!', help='Network Insight Admin Password')
    parser.add_argument('-F', '--filename', default='new-vrni-metrics', help='filename')

    args = parser.parse_args()

    get_vrni_metrics(args.hostname, args.username, args.password, args.filename)