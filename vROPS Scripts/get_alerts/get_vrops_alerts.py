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
            "1. ???????????????",
            "2. ??????",
            "3. ?????????",
            "4. ?????????",
            "5. ?????????",
            "6. ?????????",
            "7. ?????? ??????",
            "8. ?????? ??????",
            "9. ?????? ??????",
            "10. ??????",
            "11. ?????? ID"
        ]
    )

    # Write alert into excel
    for alert in alerts:

        #print("########## Writing the following alert to the csv file : "+ alert['name'])

        # Alert Array to each row
        array = []

        # 1. ????????? ?????? ###
        array.append(alert['adapterKindKey'])

        # 2. ?????? ###
        array.append(alert['resourceKindKey'])

        # 3. ????????? ###
        if alert['type'] == 15:
            alert_type = '??????????????????'
        if alert['type'] == 16:
            alert_type = '?????????/??????????????????'
        if alert['type'] == 17:
            alert_type = '????????????'
        if alert['type'] == 18:
            alert_type = '????????????'
        if alert['type'] == 19:
            alert_type = '????????????'
        array.append(alert_type)

        # 4. ????????? ###
        if alert['subType'] == 18:
            alert_subtype = '?????????'
        if alert['subType'] == 19:
            alert_subtype = '??????'
        if alert['subType'] == 20:
            alert_subtype = '??????'
        if alert['subType'] == 21:
            alert_subtype = '????????????'
        if alert['subType'] == 22:
            alert_subtype = '??????'
        array.append(alert_subtype)

        # 5. ?????????
        if alert['states'][0]['impact']['detail'] == 'health':
            alert_impact = '??????'
        if alert['states'][0]['impact']['detail'] == 'risk':
            alert_impact = '??????'
        if alert['states'][0]['impact']['detail'] == 'efficiency':
            alert_impact = '?????????'
        array.append(alert_impact)

        # 6. ?????????
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
                    alert_severity += '??????' + "\n"
                if symptom_serverity == 'IMMEDIATE':
                    alert_severity += '??????' + "\n"
                if symptom_serverity == 'WARNING':
                    alert_severity += '??????' + "\n"
                if symptom_serverity == 'INFORMATION':
                    alert_severity += '??????' + "\n"
                if symptom_serverity == 'AUTO':
                    alert_severity += '????????? ?????????' + "\n"

        if alert['states'][0]['severity'] == 'CRITICAL':
            alert_severity = '??????'
        if alert['states'][0]['severity'] == 'IMMEDIATE':
            alert_severity = '??????'
        if alert['states'][0]['severity'] == 'WARNING':
            alert_severity = '??????'
        if alert['states'][0]['severity'] == 'INFORMATION':
            alert_severity = '??????'
        array.append(alert_severity)

        # 7. ?????? ??????
        array.append(alert['name'])

        # 8. ?????? ??????
        if 'description' in alert:
            array.append(alert['description'])
        else:
            array.append(" ")

        # 9. ?????? ??????
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

        # 10. ??????
        symptomset_string = "?????? ??????" + "\n"

        # ?????? ??????
        if 'operator' in alert['states'][0]['base-symptom-set']:
            symptomset_string = symptomset_string + "operator: " + alert['states'][0]['base-symptom-set']['operator'] + "\n"

        # ?????? ????????? ????????? ?????? ??????
        if 'symptom-sets' in alert['states'][0]['base-symptom-set']:
            symptomset_number = 1
            for symptom in alert['states'][0]['base-symptom-set']['symptom-sets']:
                symptomset_string = symptomset_string + str(symptomset_number) + ". ?????? ??????" + "\n"
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
                        # ????????? ????????? ???
                        if '!' in symptomId:
                            # print("Symptom is inversed")
                            symptomId = symptomId.replace('!', '')
                            symptom_name = symptom_map.get(symptomId)['name']
                            symptom_adapterKindKey = symptom_map.get(symptomId)['adapterKindKey']
                            symptom_resourceKindKey = symptom_map.get(symptomId)['resourceKindKey']
                            symptom_severity = symptom_map.get(symptomId)['state']['severity']
                            if symptom_severity == 'CRITICAL':
                                symptom_severity = '??????'
                            if symptom_severity == 'IMMEDIATE':
                                symptom_severity = '??????'
                            if symptom_severity == 'WARNING':
                                symptom_severity = '??????'
                            if symptom_severity == 'INFORMATION':
                                symptom_severity = '??????'
                            if symptom_severity == 'AUTO':
                                symptom_severity = '?????? ??????'

                            symptom_state = symptom_map.get(symptomId)['state']
                            if symptom_state is not None:
                                if 'condition' in symptom_state:
                                    symptom_details = symptom_state["condition"]
                                else:
                                    symptom_details = "No condition defined"
                            else:
                                symptom_details = "No state defined"
                            symptomset_string += (
                                "?????? ??????: " + '[' + symptom_adapterKindKey + ']'
                                "[" + symptom_resourceKindKey + "]" +
                                "[" + symptom_severity + "] " +
                                symptom_name + "(" + str(symptom_details) + ")" + "\n"
                            )

                        # ???????????? ?????? ????????? ??????
                        else:
                            symptom_name = symptom_map.get(symptomId)['name']
                            symptom_adapterKindKey = symptom_map.get(symptomId)['adapterKindKey']
                            symptom_resourceKindKey = symptom_map.get(symptomId)['resourceKindKey']
                            symptom_severity = symptom_map.get(symptomId)['state']['severity']
                            if symptom_severity == 'CRITICAL':
                                symptom_severity = '??????'
                            if symptom_severity == 'IMMEDIATE':
                                symptom_severity = '??????'
                            if symptom_severity == 'WARNING':
                                symptom_severity = '??????'
                            if symptom_severity == 'INFORMATION':
                                symptom_severity = '??????'
                            if symptom_severity == 'AUTO':
                                symptom_severity = '?????? ??????'

                            symptom_state = symptom_map.get(symptomId)['state']
                            if symptom_state is not None:
                                if 'condition' in symptom_state:
                                    symptom_details = symptom_state["condition"]
                                else:
                                    symptom_details = "No condition defined"
                            else:
                                symptom_details = "No state defined"
                            symptomset_string += (
                                "?????? ??????: " + '[' + symptom_adapterKindKey + ']'
                                "[" + symptom_resourceKindKey + "] " +
                                "[" + symptom_severity + "]" +
                                symptom_name + "(" + str(symptom_details) + ")" + "\n"
                            )
                symptomset_number += 1

        # ?????? ????????? ????????? ??????
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
                    # ????????? ????????? ??????
                    if '!' in symptomId:
                            symptomId = symptomId.replace('!', '')
                            symptom_name = symptom_map.get(symptomId)['name']
                            symptom_adapterKindKey = symptom_map.get(symptomId)['adapterKindKey']
                            symptom_resourceKindKey = symptom_map.get(symptomId)['resourceKindKey']
                            symptom_severity = symptom_map.get(symptomId)['state']['severity']
                            if symptom_severity == 'CRITICAL':
                                symptom_severity = '??????'
                            if symptom_severity == 'IMMEDIATE':
                                symptom_severity = '??????'
                            if symptom_severity == 'WARNING':
                                symptom_severity = '??????'
                            if symptom_severity == 'INFORMATION':
                                symptom_severity = '??????'
                            if symptom_severity == 'AUTO':
                                symptom_severity = '?????? ??????'

                            symptom_state = symptom_map.get(symptomId)['state']
                            if 'symptom_state' != "":
                                if 'condition' in symptom_state:
                                    symptom_details = symptom_state["condition"]
                                else:
                                    symptom_details = "No condition defined"
                            else:
                                symptom_details = "No state defined"

                            symptomset_string += (
                                "?????? ??????: (?????????)" +  '['+ symptom_adapterKindKey + ']'
                                "[" + symptom_resourceKindKey + "] " +
                                "[" + symptom_severity + "] " +
                                symptom_name +  "(" + str(symptom_details) + ")" + "\n"
                            )
                    # ???????????? ?????? ????????? ??????
                    else:
                            symptom_name = symptom_map.get(symptomId)['name']
                            symptom_adapterKindKey = symptom_map.get(symptomId)['adapterKindKey']
                            symptom_resourceKindKey = symptom_map.get(symptomId)['resourceKindKey']
                            symptom_severity = symptom_map.get(symptomId)['state']['severity']
                            if symptom_severity == 'CRITICAL':
                                symptom_severity = '??????'
                            if symptom_severity == 'IMMEDIATE':
                                symptom_severity = '??????'
                            if symptom_severity == 'WARNING':
                                symptom_severity = '??????'
                            if symptom_severity == 'INFORMATION':
                                symptom_severity = '??????'
                            if symptom_severity == 'AUTO':
                                symptom_severity = '?????? ??????'

                            symptom_state = symptom_map.get(symptomId)['state']
                            if symptom_state is not None:
                                if 'condition' in symptom_state:
                                    symptom_details = symptom_state["condition"]
                                else:
                                    symptom_details = "No condition defined"
                            else:
                                symptom_details = "No state defined"

                            symptomset_string += (
                                "?????? ??????: " +  '['+ symptom_adapterKindKey + ']'
                                "[" + symptom_resourceKindKey + "] " +
                                "[" + symptom_severity + "] " +
                                symptom_name +  "(" + str(symptom_details) + ")" + "\n"
                            )

        array.append(symptomset_string)

        # 11. ?????? ID
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
