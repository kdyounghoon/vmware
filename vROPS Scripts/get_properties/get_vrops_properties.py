#!/usr/bin/python
# -*- coding: utf-8
import requests
import json
import csv
import urllib3
import math
import argparse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

base_url_tmp = 'https://%s'
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

def get_vrops_metrics(vrops_url, username, password, filename):



    # Login
    print("### Logging into " + vrops_url)
    base_url = base_url_tmp % vrops_url
    data= {
        "username": username,
        "authSource": "Local",
        "password": password
    }
    resp = requests.post(
        base_url + '/suite-api/api/auth/token/acquire',
        headers=headers, json=data,
        verify=False)
    resp.raise_for_status()
    headers['Authorization'] = 'vRealizeOpsToken ' + resp.json()['token']
    print("### Logged into " + vrops_url)

 
    #headers['Accept-Language'] = "ko"

    ##Get Adapter Kinds
    resp = requests.get(
        base_url + '/suite-api/api/adapterkinds/NSXTAdapter/resourcekinds/',
        headers=headers,
        verify=False)
    resp.raise_for_status()
    resourceKinds = resp.json()['resource-kind']


    filename = "vrops_nsxt_property" + ".csv"
    f = open(filename, 'w', newline='', encoding='utf-8-sig')
    pwr = csv.writer(f)
    pwr.writerow(["resoureceKind", "attribute", "key", "name", "description", "dataType"])


    for resourceKind in resourceKinds:
        resourceKind_name = resourceKind['key']
        propertyUrl = resourceKind['links'][2]['href']
    
        p_resp = requests.get(
            base_url + propertyUrl,
            headers=headers,
            verify=False)
        p_resp.raise_for_status()
        properties = p_resp.json()['resourceTypeAttributes']


        for res_property in properties:

            #print("########## Writing the following alert to the csv file : "+ alert['name'])
            # Alert Array to each row
            array = []

            array.append(resourceKind_name)

            array.append("property")

            array.append(res_property['key'])

            array.append(res_property['name'])

            array.append(res_property['description'])

            if 'dataType' in res_property:
                array.append(res_property['dataType'])
            
            print("Writing Property for ---> " + resourceKind_name + " " + res_property['name']) 

            pwr.writerow(array)




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--hostname', default='vrops80-weekly.cmbu.local', help='vRealize Operations IP or Hostname')
    parser.add_argument('-U', '--username', default='admin', help='vRealize Operations Admin Username')
    parser.add_argument('-P', '--password', default='VMware1!', help='vRealize Operations Admin Password')
    parser.add_argument('-F', '--filename', default='vrops-metrics', help='filename')

    args = parser.parse_args()

    get_vrops_metrics(args.hostname, args.username, args.password, args.filename)
