#!/usr/bin/python
# -*- coding: utf-8
import requests
import json
import csv
import logging
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

    # Get Alerts
    headers['Accept-Language'] = "ko"
    resp = requests.get(
        base_url + '/alertdefinitions?pageSize=2000',
        headers=headers, json=data,
        verify=False)
    resp.raise_for_status()
    alerts = resp.json()['alertDefinitions']
    print("### Total Number of Alerts: " + str(resp.json()['pageInfo']['totalCount']))

    number_of_alerts = 0
    total_number_of_alerts = json.loads(resp.text)['pageInfo']['totalCount']

    # Get Symptoms
    resp = requests.get(
        base_url + '/symptomdefinitions?pageSize=2000',
        headers=headers, json=data,
        verify=False)
    resp.raise_for_status()
    symptoms = resp.json()['symptomDefinitions']

    # Create Symptom Map with Symptom Id and Name
    symptom_map = {}
    for symptom in symptoms:
        sym_data = {
            symptom['id']: {
                'name': symptom['name'],
                'adapterKindKey':  symptom['adapterKindKey'],
                'resourceKindKey': symptom['resourceKindKey'],
                'state': symptom['state']}
            }
        symptom_map.update(sym_data)

    # Get Recommendations
    resp = requests.get(
        base_url + '/recommendations?pageSize=2000',
        headers=headers, json=data,
        verify=False)
    resp.raise_for_status()
    recommendations = resp.json()['recommendations']

    recommendation_map = {}
    for recommendation in recommendations:
        rec_data = {
            recommendation['id']: recommendation['description']
        }
        recommendation_map.update(rec_data)

    # Write Column Definitions
    wr.writerow(
        [
            "1. 어댑터소스",
            "2. 개체",
            "3. 대분류",
            "4. 중분류",
            "5. 영향도",
            "6. 중요도",
            "7. 경고 이름",
            "8. 경고 설명",
            "9. 권고 사항",
            "10. 증상",
            "11. 경고 ID"
        ]
    )

    # Write alert into excel
    for alert in alerts:

        #print("########## Writing the following alert to the csv file : "+ alert['name'])

        # Alert Array to each row
        array = []

        # 1. 어댑터 소스 ###
        array.append(alert['adapterKindKey'])

        # 2. 개체 ###
        array.append(alert['resourceKindKey'])

        # 3. 대분류 ###
        if alert['type'] == 15:
            alert_type = '애플리케이션'
        if alert['type'] == 16:
            alert_type = '가상화/하이퍼바이저'
        if alert['type'] == 17:
            alert_type = '하드웨어'
        if alert['type'] == 18:
            alert_type = '스토리지'
        if alert['type'] == 19:
            alert_type = '네트워크'
        array.append(alert_type)

        # 4. 중분류 ###
        if alert['subType'] == 18:
            alert_subtype = '가용성'
        if alert['subType'] == 19:
            alert_subtype = '성능'
        if alert['subType'] == 20:
            alert_subtype = '용량'
        if alert['subType'] == 21:
            alert_subtype = '규정준수'
        if alert['subType'] == 22:
            alert_subtype = '구성'
        array.append(alert_subtype)

        # 5. 영향도
        if alert['states'][0]['impact']['detail'] == 'health':
            alert_impact = '상태'
        if alert['states'][0]['impact']['detail'] == 'risk':
            alert_impact = '위험'
        if alert['states'][0]['impact']['detail'] == 'efficiency':
            alert_impact = '효율성'
        array.append(alert_impact)

        # 6. 중요도
        alert_severity = ''
        symptom_serverity_list = []
        if alert['states'][0]['severity'] == 'AUTO':
            if 'symptom-sets' in alert['states'][0]['base-symptom-set']:
                for symptom in alert['states'][0]['base-symptom-set']['symptom-sets']:
                    if 'symptomDefinitionIds' in symptom:
                        for symptomId in symptom['symptomDefinitionIds']:
                            if '!' in symptomId:
                                #print("Symptom is inversed")
                                symptomId = symptomId.replace('!', '')
                                symptom_state = symptom_map.get(symptomId)['state']
                                symptom_severity = symptom_state["severity"]
                                symptom_serverity_list.append(symptom_severity)
                            else:
                                symptom_state = symptom_map.get(symptomId)['state']
                                symptom_severity = symptom_state["severity"]
                                symptom_serverity_list.append(symptom_severity)
            else:
                for symptomId in alert['states'][0]['base-symptom-set']['symptomDefinitionIds']:
                    if '!' in symptomId:
                            #print("Symptom is inversed")
                            symptomId = symptomId.replace('!', '')
                            symptom_state = symptom_map.get(symptomId)['state']
                            symptom_severity = symptom_state["severity"]
                            symptom_serverity_list.append(symptom_severity)
                    else:
                            symptom_state = symptom_map.get(symptomId)['state']
                            symptom_severity = symptom_state["severity"]
                            symptom_serverity_list.append(symptom_severity)

            symptom_serverity_list = list(set(symptom_serverity_list))

            for symptom_serverity in symptom_serverity_list:
                if symptom_serverity == 'CRITICAL':
                    alert_severity += '위험' + "\n"
                if symptom_serverity == 'IMMEDIATE':
                    alert_severity += '즉시' + "\n"
                if symptom_serverity == 'WARNING':
                    alert_severity += '경고' + "\n"
                if symptom_serverity == 'INFORMATION':
                    alert_severity += '정보' + "\n"
                if symptom_serverity == 'AUTO':
                    alert_severity += '메시지 이벤트' + "\n"

        if alert['states'][0]['severity'] == 'CRITICAL':
            alert_severity = '위험'
        if alert['states'][0]['severity'] == 'IMMEDIATE':
            alert_severity = '즉시'
        if alert['states'][0]['severity'] == 'WARNING':
            alert_severity = '경고'
        if alert['states'][0]['severity'] == 'INFORMATION':
            alert_severity = '정보'
        array.append(alert_severity)

        # 7. 경고 이름
        array.append(alert['name'])

        # 8. 경고 설명
        if 'description' in alert:
            array.append(alert['description'])
        else:
            array.append(" ")

        # 9. 권고 사항
        if 'recommendationPriorityMap' in alert['states'][0]:
            recommendations = alert['states'][0]['recommendationPriorityMap']
            recommendations_string = ""
            recommendation_number = 1
            for recommendation in recommendations.keys():
                recommendations_name = recommendation_map.get(recommendation)
                recommendations_name = recommendations_name.replace("<a href=", "");
                recommendations_name = recommendations_name.replace("\"", "");
                recommendations_name = recommendations_name.replace("</a>", "");
                recommendations_name = recommendations_name.replace("rel=", "");
                recommendations_name = recommendations_name.replace("nofollow", "");
                recommendations_name = recommendations_name.replace(">", "");
                recommendations_name = recommendations_name.replace("<br", "");
                recommendations_string = recommendations_string  + "\n" + str(recommendation_number) + ". " + recommendations_name
                recommendation_number = recommendation_number + 1
            array.append(recommendations_string)
        else:
            array.append(" ")

        # 10. 증상
        symptomset_string = "증상 조건" + "\n"

        # 증상 조건
        if 'operator' in alert['states'][0]['base-symptom-set']:
            symptomset_string = symptomset_string + "operator: " + alert['states'][0]['base-symptom-set']['operator'] + "\n"

        # 증상 묶음이 여려개 있을 경우
        if 'symptom-sets' in alert['states'][0]['base-symptom-set']:
            symptomset_number = 1
            for symptom in alert['states'][0]['base-symptom-set']['symptom-sets']:
                symptomset_string = symptomset_string + str(symptomset_number) + ". 증상 묶음" + "\n"
                if 'relation' in symptom:
                    symptomset_string = symptomset_string + "relation: " + symptom['relation'] + "\n"
                if 'aggregation' in symptom:
                    symptomset_string = symptomset_string + "aggregation: " + symptom['aggregation'] + "\n"
                if 'symptomSetOperator' in symptom:
                    symptomset_string = symptomset_string + "symptomSetOperator: " + symptom['symptomSetOperator'] + "\n"
                if 'populationOperator' in symptom:
                    symptomset_string = symptomset_string + "populationOperator: " + symptom['populationOperator'] + "\n"
                if 'value' in symptom:
                    symptomset_string = symptomset_string + "value: " + str(symptom['value']) + "\n"
                if 'symptomDefinitionIds' in symptom:
                    for symptomId in symptom['symptomDefinitionIds']:
                        # 반전된 증상일 경
                        if '!' in symptomId:
                            # print("Symptom is inversed")
                            symptomId = symptomId.replace('!', '')
                            symptom_name = symptom_map.get(symptomId)['name']
                            symptom_adapterKindKey = symptom_map.get(symptomId)['adapterKindKey']
                            symptom_resourceKindKey = symptom_map.get(symptomId)['resourceKindKey']
                            symptom_severity = symptom_map.get(symptomId)['state']['severity']
                            if symptom_severity == 'CRITICAL':
                                symptom_severity = '위험'
                            if symptom_severity == 'IMMEDIATE':
                                symptom_severity = '즉시'
                            if symptom_severity == 'WARNING':
                                symptom_severity = '경고'
                            if symptom_severity == 'INFORMATION':
                                symptom_severity = '정보'
                            if symptom_severity == 'AUTO':
                                symptom_severity = '증상 기준'

                            symptom_state = symptom_map.get(symptomId)['state']
                            if symptom_state is not None:
                                if 'condition' in symptom_state:
                                    symptom_details = symptom_state["condition"]
                                else:
                                    symptom_details = "No condition defined"
                            else:
                                symptom_details = "No state defined"
                            symptomset_string += (
                                "증상 이름: " + '[' + symptom_adapterKindKey + ']'
                                "[" + symptom_resourceKindKey + "]" +
                                "[" + symptom_severity + "] " +
                                symptom_name + "(" + str(symptom_details) + ")" + "\n"
                            )

                        # 반전되지 않은 증상일 경우
                        else:
                            symptom_name = symptom_map.get(symptomId)['name']
                            symptom_adapterKindKey = symptom_map.get(symptomId)['adapterKindKey']
                            symptom_resourceKindKey = symptom_map.get(symptomId)['resourceKindKey']
                            symptom_severity = symptom_map.get(symptomId)['state']['severity']
                            if symptom_severity == 'CRITICAL':
                                symptom_severity = '위험'
                            if symptom_severity == 'IMMEDIATE':
                                symptom_severity = '즉시'
                            if symptom_severity == 'WARNING':
                                symptom_severity = '경고'
                            if symptom_severity == 'INFORMATION':
                                symptom_severity = '정보'
                            if symptom_severity == 'AUTO':
                                symptom_severity = '증상 기준'

                            symptom_state = symptom_map.get(symptomId)['state']
                            if symptom_state is not None:
                                if 'condition' in symptom_state:
                                    symptom_details = symptom_state["condition"]
                                else:
                                    symptom_details = "No condition defined"
                            else:
                                symptom_details = "No state defined"
                            symptomset_string += (
                                "증상 이름: " + '[' + symptom_adapterKindKey + ']'
                                "[" + symptom_resourceKindKey + "] " +
                                "[" + symptom_severity + "]" +
                                symptom_name + "(" + str(symptom_details) + ")" + "\n"
                            )
                symptomset_number += 1

        # 증상 묶음이 하나일 경우
        else:
            if 'aggregation' in alert['states'][0]['base-symptom-set']:
                symptomset_string = symptomset_string + "aggregation: " + alert['states'][0]['base-symptom-set']['aggregation'] + "\n"
            if 'symptomSetOperator' in alert['states'][0]['base-symptom-set']:
                symptomset_string = symptomset_string + "symptomSetOperator: " + alert['states'][0]['base-symptom-set']['symptomSetOperator'] + "\n"
            if 'populationOperator' in alert['states'][0]['base-symptom-set']:
                symptomset_string = symptomset_string + "populationOperator: " + alert['states'][0]['base-symptom-set']['populationOperator'] + "\n"
            if 'value' in alert['states'][0]['base-symptom-set']:
                symptomset_string = symptomset_string + "value: " + str(alert['states'][0]['base-symptom-set']['value']) + "\n"
            if 'relation' in alert['states'][0]['base-symptom-set']:
                symptomset_string = symptomset_string + "relation: " + alert['states'][0]['base-symptom-set']['relation'] + "\n"
            if 'symptomDefinitionIds' in alert['states'][0]['base-symptom-set']:
                for symptomId in alert['states'][0]['base-symptom-set']['symptomDefinitionIds']:
                    # 반전된 증상일 경우
                    if '!' in symptomId:
                            symptomId = symptomId.replace('!', '')
                            symptom_name = symptom_map.get(symptomId)['name']
                            symptom_adapterKindKey = symptom_map.get(symptomId)['adapterKindKey']
                            symptom_resourceKindKey = symptom_map.get(symptomId)['resourceKindKey']
                            symptom_severity = symptom_map.get(symptomId)['state']['severity']
                            if symptom_severity == 'CRITICAL':
                                symptom_severity = '위험'
                            if symptom_severity == 'IMMEDIATE':
                                symptom_severity = '즉시'
                            if symptom_severity == 'WARNING':
                                symptom_severity = '경고'
                            if symptom_severity == 'INFORMATION':
                                symptom_severity = '정보'
                            if symptom_severity == 'AUTO':
                                symptom_severity = '증상 기준'

                            symptom_state = symptom_map.get(symptomId)['state']
                            if 'symptom_state' != "":
                                if 'condition' in symptom_state:
                                    symptom_details = symptom_state["condition"]
                                else:
                                    symptom_details = "No condition defined"
                            else:
                                symptom_details = "No state defined"

                            symptomset_string += (
                                "증상 이름: (반전됨)" +  '['+ symptom_adapterKindKey + ']'
                                "[" + symptom_resourceKindKey + "] " +
                                "[" + symptom_severity + "] " +
                                symptom_name +  "(" + str(symptom_details) + ")" + "\n"
                            )
                    # 반전되지 않은 증상일 경우
                    else:
                            symptom_name = symptom_map.get(symptomId)['name']
                            symptom_adapterKindKey = symptom_map.get(symptomId)['adapterKindKey']
                            symptom_resourceKindKey = symptom_map.get(symptomId)['resourceKindKey']
                            symptom_severity = symptom_map.get(symptomId)['state']['severity']
                            if symptom_severity == 'CRITICAL':
                                symptom_severity = '위험'
                            if symptom_severity == 'IMMEDIATE':
                                symptom_severity = '즉시'
                            if symptom_severity == 'WARNING':
                                symptom_severity = '경고'
                            if symptom_severity == 'INFORMATION':
                                symptom_severity = '정보'
                            if symptom_severity == 'AUTO':
                                symptom_severity = '증상 기준'

                            symptom_state = symptom_map.get(symptomId)['state']
                            if symptom_state is not None:
                                if 'condition' in symptom_state:
                                    symptom_details = symptom_state["condition"]
                                else:
                                    symptom_details = "No condition defined"
                            else:
                                symptom_details = "No state defined"

                            symptomset_string += (
                                "증상 이름: " +  '['+ symptom_adapterKindKey + ']'
                                "[" + symptom_resourceKindKey + "] " +
                                "[" + symptom_severity + "] " +
                                symptom_name +  "(" + str(symptom_details) + ")" + "\n"
                            )

        array.append(symptomset_string)

        # 11. 경고 ID
        array.append(alert['id'])


        # Write this Alert to CSV File
        wr.writerow(array)

        #print("########## Finished writing the following alert to the csv file : "+ alert['name'])
        number_of_alerts = number_of_alerts + 1
        #print("Total Number of Alerts Written: " + str(number_of_alerts))
        completion_rate = math.ceil(number_of_alerts / total_number_of_alerts * 100)
        #print("Completion Rate: " + str(completion_rate) + "%")
    print("### Total Number of Alerts Written: " + str(number_of_alerts))
    print("### Filename is : " + filename + ".csv")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--hostname', default='172.20.10.61', help='vRealize Operations IP or Hostname')
    parser.add_argument('-U', '--username', default='admin', help='vRealize Operations Admin Username')
    parser.add_argument('-P', '--password', default='VMware1!', help='vRealize Operations Admin Password')
    parser.add_argument('-F', '--filename', default='horiozn-vrops-alerts', help='filename')

    args = parser.parse_args()

    get_vrops_alerts(args.hostname, args.username, args.password, args.filename)
