#!/usr/bin/python
# -*- coding: utf-8
import requests
import json
import csv
import argparse
import urllib3
import html2text


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

base_url_tmp = 'https://%s'
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

def get_vrni_alerts(vrni_url, username, password, filename):

    base_url = base_url_tmp % vrni_url
    # Open CSV file for writing alerts
    f = open(filename + '.csv','w', newline='', encoding='utf-8-sig')
    wr = csv.writer(f)
    #  Login
    print("### Login into vRNI: " + vrni_url)

    data= {
    "username": "ykwak@vmware.com",
    "password": "Rhkrdudgns0105^",
    "domain": {
        "domain_type": "LDAP",
        "value": "vmware.com"
        }
    }

    resp = requests.post(
        base_url + '/api/ni/auth/token',
        headers=headers, json=data,
        verify=False)
    resp.raise_for_status()


    headers['Authorization'] = 'NetworkInsight ' + resp.json()['token']
    print("### Logged into vrni: " + vrni_url)


    # Get Alerts
    resp = requests.get(
        base_url + '/api/ni/schema/problems',
        headers=headers,
        verify=False)
    resp.raise_for_status()
    alerts = resp.json()['results']

    wr.writerow(["1. Entity", "2. 경고 이름", "3. 경고 설명", "4. 심각도", "5. 태그", "6. supported_entity_types", "7. supported_manager_types", "8. impact", "9. recommendations"])

    number_of_alerts = 1
    for alert in alerts:
        # Alert
        array = []

        # 1. 컨텐트팩 #
        array.append(alert['entity_type'])

        # 2. 경고 이름 #
        array.append(alert['name'])

        # 3. 경고 설명 #
        array.append(alert['help_text'])

        # 4. 권장 사항 #
        if 'severity' in alert:
            array.append(alert['severity'])
     

        # 5. 참고 쿼리
        if alert['tags'] is not None:
            array.append(alert['tags'])

        if alert['supported_entity_types'] is not None:
            array.append(alert['supported_entity_types'])
        
        if alert['supported_manager_types'] is not None:
            array.append(alert['supported_manager_types'])

        if 'impact' in alert:
            array.append(alert['impact'])

        if alert['recommendations'] is not None:
            array.append(alert['recommendations'])


        wr.writerow(array)
        number_of_alerts += 1

    print("### The number of alerts written " + str(number_of_alerts))
  


 
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--hostname', default='field-demo.vrni.cmbu.local', help='vRealize Network Insight')
    parser.add_argument('-U', '--username', default='admin', help='vRealize Network Insight Admin Username')
    parser.add_argument('-P', '--password', default='VMware1!', help='Network Insight Admin Password')
    parser.add_argument('-F', '--filename', default='vrni-alerts', help='filename')

    args = parser.parse_args()

    get_vrni_alerts(args.hostname, args.username, args.password, args.filename)