import requests
import json
import csv
import logging
import urllib3
import html2text


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_HOST = 'https://192.168.1.113'
header = {'Content-Type':'application/json'}
# #  Request vRLI API function # # # #
def req(path, query, method, header, data={}):
    url = API_HOST + path
    #print('HTTP Method: %s' % method)
    print('Request URL: %s' % url)
    if method == 'GET':
        try:
            response = requests.get(url, headers=header, verify=False)
        except requests.exceptions.RequestException as e:  
            raise SystemExit(e)
        except requests.exceptions.HTTPError as e:  
            raise SystemExit(e)
    elif method == 'POST' :
        try:
            response = requests.post(url, headers=header, data=data, verify=False)
        except requests.exceptions.ConnectionError as e:  
            raise SystemExit(e)
    elif method == 'PATCH' :
        try:
            response = requests.patch(url, headers=header, data=data, verify=False)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)
        except requests.exceptions.HTTPError as e:  
            raise SystemExit(e)
    if response.status_code != 200:
        response_raw = json.loads(response.content)
        logging.error("API Call Failed: Status code is as follow ======>> " + response_raw)
        raise SystemExit(response.status_code)
    return response

header = {}
def auth():
    global header 
    header = {"content-type": "application/json","Accept":"application/json"}
    data= {
        "username" : "admin",
        "provider": "Local",
        "password" : "VMware1!"
    }
    credential = json.dumps(data)
    resp = req('/api/v1/sessions', '', 'POST', header, credential)
    get_token = json.loads(resp.text)
    token = get_token['sessionId']
    if token:
        header = {
            "content-type": "application/json",
            "Accept":"application/json", 
            "Accept-Language":"ko", 
            "Authorization" : "Bearer " + token
    }
    
# authenticate
auth()

# Get Alerts
resp = req('/api/v1/alerts', '', 'GET', header, '')
alerts = json.loads(resp.text)


f = open('vrli_alerts06.csv','w', newline='', encoding='utf-8-sig')
fo = open('vrli-original.csv','r', encoding='utf-8-sig')
rr = csv.reader(fo)
wr = csv.writer(f)
wr.writerow(["1. 컨텐트팩", "2. 대분류", "3. 중분류", "4. 경고 이름", "5. 경고 설명", "6. 권장 사항", "7. 참고쿼리"])

category_map = {}
csvfile =  open('vrli-original.csv','r', encoding='utf-8-sig') 
alert_reader = csv.reader(csvfile, delimiter=',')

for row in alert_reader:
    category_map.update({row[3] : [row[1], row[2]]})

#  ExtractedFields을 위한 HashMap 생성
extractedField_map = {}
for alert in alerts:
    chartQuery = json.loads(alert['chartQuery'])
    if 'extractedFields' in chartQuery:
        for extractedField in chartQuery['extractedFields']:
            data = {extractedField['internalName'] : extractedField['displayName']}
            extractedField_map.update(data)
    
for alert in alerts:
    # Alert
    array = []
   
    # 1. 컨텐트팩 # 
    array.append(alert['contentPackName']) 
    
    # 2. 대분류 #
    array.append(category_map.get(alert['name'])[0])
                 
    # 3. 중분류 #
    array.append(category_map.get(alert['name'])[1])
    
    # 4. 경고 이름 #
    array.append(alert['name'])
    
    # 5. 경고 설명 #
    h = html2text.HTML2Text() #  HTML 파일 형식을 TEXT 형식으로 변환
    
    if 'info' in alert:
        array.append(h.handle(alert['info']))
    else:
        array.append(" ")
    
    # 6. 권장 사항 #
    if 'recommendation' in alert:
        array.append(alert['recommendation'])  
    else:
        array.append(" ")
    
    # 7. 참고 쿼리 
    chartQuery = json.loads(alert['chartQuery'])
    chartQuery_string = ""
    
    # 전체 TEXT 쿼리 
    if chartQuery['query'] != "":
        chartQuery_string += "Text Query: " + chartQuery['query'] + "\n"
        
    # 필드 조건 AND/OR 
    chartQuery_string += "Field Constraints Condition: " + chartQuery['constraintToggle'] + "\n"
    
    # 필드 상세
    if 'fieldConstraints' in chartQuery:
        fieldConstraints = chartQuery['fieldConstraints']
        field_number = 1
        for fieldConstraint in fieldConstraints:
            internalName = fieldConstraint['internalName']
            operator = fieldConstraint['operator']
            if 'value' in fieldConstraint:
                value = fieldConstraint['value']
            else: 
                value = " "
            if int(len(internalName)) > 20:
                if extractedField_map.get(internalName) is not None:
                    chartQuery_string +=  str(field_number) + ". [field] " + extractedField_map.get(internalName) + " [operator] " + operator + " [value] " + str(value) + "\n"
                else: 
                    chartQuery_string +=  str(field_number) + ". [field] " + internalName + " [operator] " + operator + " [value] " + str(value) + "\n"
            else:
                chartQuery_string +=  str(field_number) + ". [field] " + internalName + " [operator] " + operator + " [value] " + str(value) + "\n"
            field_number += 1       
    array.append(chartQuery_string)
    
    wr.writerow(array)
