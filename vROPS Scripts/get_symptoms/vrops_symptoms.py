#!/usr/bin/python
# -*- coding: utf-8
import requests
import json
import csv
import urllib3
import math
import argparse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

base_url_tmp = 'https://%s/suite-api/api'
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

def get_vrops_alerts(vrops_url, username, password, filename):

    # Open CSV File for saving vROPs alerts
    filename = filename + ".csv"
    f = open(filename, 'w', newline='', encoding='utf-8-sig')
    wr = csv.writer(f)

    # Login
    print("### Logging into " + vrops_url)
    base_url = base_url_tmp % vrops_url
    data= {
        "username": username,
        "authSource": "Local",
        "password": password
    }
    resp = requests.post(
        base_url + '/auth/token/acquire',
        headers=headers, json=data,
        verify=False)
    resp.raise_for_status()
    headers['Authorization'] = 'vRealizeOpsToken ' + resp.json()['token']
    print("### Logged into " + vrops_url)

    # # Get Alerts
    headers['Accept-Language'] = "ko"
    # resp = requests.get(
    #     base_url + '/alertdefinitions?pageSize=2000',
    #     headers=headers, json=data,
    #     verify=False)
    # resp.raise_for_status()
    # alerts = resp.json()['alertDefinitions']
    # print("### Total Number of Alerts: " + str(resp.json()['pageInfo']['totalCount']))

    # number_of_alerts = 0
    # total_number_of_alerts = json.loads(resp.text)['pageInfo']['totalCount']

    # Get Symptoms
    resp = requests.get(
        base_url + '/symptomdefinitions?pageSize=2000',
        headers=headers, json=data,
        verify=False)
    resp.raise_for_status()
    symptoms = resp.json()['symptomDefinitions']

    # Create Symptom Map with Symptom Id and Name
    # symptom_map = {}
    # for symptom in symptoms:
    #     sym_data = {
    #         symptom['id']: {
    #             'name': symptom['name'],
    #             'adapterKindKey':  symptom['adapterKindKey'],
    #             'resourceKindKey': symptom['resourceKindKey'],
    #             'state': symptom['state']}
    #         }
    #     symptom_map.update(sym_data)


    # Write Column Definitions
    wr.writerow(
        [
            "1. ID",
            "2. 이름",
            "3. 어댑터",
            "4. 개체유형",
            "5. 대기주기",
            "6. 취소주기",
            "7. 중요도",
            "8. 조건"
            "9. 증상유형",
            "10. 메트릭",
            "11. 연산자 ",
            "12. 임계치",
            "13. 임계치 타입",
            "14. 인스턴스화",
            "15. 임게치 유형"
        ]
    )

    # Write alert into excel
    for symptom in symptoms:

        #print("########## Writing the following alert to the csv file : "+ alert['name'])

        # Alert Array to each row
        array = []

        # 1. ID ###
        array.append(symptom['id'])

        # 2. 이름 ###
        array.append(symptom['name'])

        # 3. 개체유형 ###
        array.append(symptom['adapterKindKey'])

        # 4. 어댑터유형 ###
        array.append(symptom['resourceKindKey'])

        # 5. 대기주기 ###
        array.append(symptom['waitCycles'])

        # 6. 취소주기 ###
        array.append(symptom['cancelCycles'])

        # 7. 중요도 ###
        array.append(symptom['state']['severity'])

        #8. 조건 ###
        if 'condition' in symptom['state']:
            if symptom['state']['condition']['type'] == "CONDITION_HT":
                array.append(symptom['state']['condition']['type'])
                array.append(symptom['state']['condition']['key'])
                array.append(symptom['state']['condition']['operator'])
                array.append(symptom['state']['condition']['value'])
                array.append(symptom['state']['condition']['valueType'])
                array.append(symptom['state']['condition']['instanced'])
                array.append(symptom['state']['condition']['thresholdType'])
                if 'targetKey' in symptom['state']['condition']:
                    array.append(symptom['state']['condition']['targetKey'])
                wr.writerow(array)
        #     else:
        #         array.append(symptom['state']['condition']['type'])
            
        # else:
        #     array.append(symptom['state'])


        # wr.writerow(array)
        





   


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--hostname', default='192.168.36.171', help='vRealize Operations IP or Hostname')
    parser.add_argument('-U', '--username', default='admin', help='vRealize Operations Admin Username')
    parser.add_argument('-P', '--password', default='VMware1!', help='vRealize Operations Admin Password')
    parser.add_argument('-F', '--filename', default='vrops-symptoms-condition-ht', help='filename')

    args = parser.parse_args()

    get_vrops_alerts(args.hostname, args.username, args.password, args.filename)
