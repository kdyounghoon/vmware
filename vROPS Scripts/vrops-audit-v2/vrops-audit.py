
'''
Created on 2019. 11. 12.

@author: jzide
'''

import re
import sys
import time
import json
import openpyxl
import requests
import argparse
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

base_url_tmp = 'https://%s/suite-api/api'
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

def create_audit(vrops_url, username, password, page_size, exec_timestamp, interval_type, range_type, range_count):
    #===============================================================================
    # Get Token
    #===============================================================================
    print('1. Login')
    base_url = base_url_tmp % vrops_url
    resp = requests.post(
        base_url + '/auth/token/acquire',
        headers=headers, json={'username': username, 'authSource': 'Local', 'password': password},
        verify=False)
    resp.raise_for_status()
    headers['Authorization'] = 'vRealizeOpsToken ' + resp.json()['token']
    print('    --> [ OK ]')
    
    #===============================================================================
    # Get VM Resource Metric
    #===============================================================================
    print('2. Get VM Metrics')
    
    resp = requests.get(
        base_url + '/resources/?pageSize=1&resourceKind=VirtualMachine',
        headers=headers,
        verify=False)
    resp.raise_for_status()
    total_count = resp.json()['pageInfo']['totalCount']
    page_count = int(total_count / page_size)
    if total_count % page_size > 0: page_count += 1
    print('  2.1 Resource Check')
    print('    Total Referred VMs : %d' % total_count)
    print('    Page Size          : %d' % page_size)
    print('    Total Pages        : %d' % page_count)
    print('    --> [ OK ]')
    
    end = int(exec_timestamp) * 1000
    if range_type == 'days':
        begin = end - (range_count * 86400000)
    elif range_type == 'hours':
        begin = end - (range_count * 3600000)
    else: raise('unsupport range type')
    
    print('  2.2 Collecting')
    resources = {}
    metrics = {}
    timestamps = []
    timestamps_raw = []
    timestamps_str = []
    for page_num in range(0, page_count):
        print('    %d page' % page_num)
        # Get Resources
        resp = requests.get(
            base_url + '/resources/?page=%d&pageSize=%d&resourceKind=VirtualMachine' % (page_num, page_size),
            headers=headers,
            verify=False)
        resp.raise_for_status()
        
        page_resources = []
        for resource in resp.json()['resourceList']:
            resources[resource['identifier']] = resource['resourceKey']['name']
            page_resources.append(resource['identifier'])
    
        # Get Metrics
        payload = {
            'begin': begin,
            'end': end,
            'intervalType': interval_type.upper(),
            'intervalQuantifier': 1,
            'rollUpType': 'AVG',
            'resourceId': page_resources,
            'statKey' : ['cpu|usage_average']
        }
        resp = requests.post(
            base_url + '/resources/stats/query?pageSize=%d' % page_size,
            headers=headers,
            json=payload,
            verify=False)
        resp.raise_for_status()
        
        for metric in resp.json()['values']:
            bucket = metric['stat-list']['stat'][0]
            bk_ts = bucket['timestamps']
            bk_vl = bucket['data']
            
            if timestamps_raw:
                for i in range(0, len(bk_ts)):
                    if timestamps_raw[0] <= bk_ts[i]:
                        timestamps_raw = bk_ts[0:i] + timestamps_raw
                        break
                for i in reversed(range(0, len(bk_ts))):
                    if timestamps_raw[-1] >= bk_ts[i]:
                        timestamps_raw = timestamps_raw + bk_ts[i+1:-1]
                        break
            else:
                timestamps_raw = bk_ts
         
            ref = {}
            for i in range(0, len(bk_ts)): ref[bk_ts[i]] = bk_vl[i]
            metrics[metric['resourceId']] = ref
    
    print('    --> [ OK ]')

    #===========================================================================
    # Write Excel     
    #===========================================================================
    print('3. Write Excel File')
    print('  3.1 Calculating Working Legend ')
    for ts in timestamps_raw:
        ts_str = time.ctime(ts / 1000.0)
        kv = re.match('(?P<day>\w+)\s+\w+\s+\d+\s+(?P<hour>\d+):', ts_str)
        if kv:
            day = kv.group('day')
            hour = int(kv.group('hour'))
            if day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'] and hour >= 8 and hour < 17:
                timestamps.append(ts)
                timestamps_str.append(ts_str)
    print('    Time Stamps   : %d' % len(timestamps))
    print('    Collected VMs : %d' % len(metrics))
    print('    --> [ OK ]')
    
    print('  3.2. Write Record')
    wb = openpyxl.Workbook()
    result = wb.active
    wb.title = 'result'
    result.append(['vCenter', 'DataCenter', 'Cluster', 'Host', 'VM Name', 'CPUs'] + timestamps_str)
       
    for resource_id, metric in metrics.items():
        try:
            resp = requests.get(
                base_url + '/resources/%s/properties' % resource_id,
                headers=headers,
                verify=False)
            for property in resp.json()['property']:
                prop_name = property['name']
                if prop_name == 'summary|parentHost':
                    prop_host = property['value']
                elif prop_name == 'summary|parentCluster':
                    prop_cluster = property['value']
                elif prop_name == 'summary|parentDatacenter':
                    prop_dc = property['value']
                elif prop_name == 'summary|parentVcenter':
                    prop_vc = property['value']
#                 elif prop_name == 'summary|runtime|powerState':
#                     prop_pw = property['value']
                elif prop_name == 'config|hardware|numCpu':
                    prop_cpu = property['value'].replace('.0', '')
        except:
            prop_host = '?'
            prop_cluster = '?'
            prop_dc = '?'
            prop_vc = '?'
#             prop_pw = '?'
            prop_cpu = '?'
        
        record = [prop_vc, prop_dc, prop_cluster, prop_host, resources[resource_id], prop_cpu]
        
        for timestamp in timestamps:
            if timestamp in metric: record.append('%.2f' % metric[timestamp])
            else: record.append('')
        result.append(record)
       
    wb.save('result-%d.xlsx' % int(time.time()))
    print('    --> [ OK ]')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--page-size', default=100, help='retrieved object count per one request')
    parser.add_argument('-e', '--execute-time', default=None, help='YYYY/MM/DD-hh:mm, default is current time, ex) 2019/11/12-15:30')
    parser.add_argument('-i', '--interval-type', default='minutes', help='[days|hours|minutes], metric intervals, default "minutes"')
    parser.add_argument('-t', '--range-type', default='days', help='[days|hours], type of before timestamp, default "days"')
    parser.add_argument('-c', '--range-count', default=1, type=int, help='count of "range-type" base, default 1')
    parser.add_argument('vrops', help='vRealize Operations IP or Hostname')
    parser.add_argument('username', help='vRealize Operations Admin Username')
    parser.add_argument('password', help='vRealize Operations Admin Password')
    args = parser.parse_args()
    
    if args.execute_time:
        kv = re.match('(?P<year>\d\d\d\d)/(?P<month>\d+)/(?P<day>\d+)-(?P<hour>\d+):(?P<minute>\d+)', args.execute_time)
        if kv:
            exec_timestamp = time.mktime((
            int(kv.group('year')),
            int(kv.group('month')),
            int(kv.group('day')),
            int(kv.group('day')),
            int(kv.group('hour')),
            int(kv.group('minute')),
            0, 0, 0))
        else:
            print('error: incorrect execute time format')
            parser.print_help()
            exit(-1)
    else:
        exec_timestamp = time.time()
    if args.interval_type not in ['days', 'hours', 'minutes']:
        print('error: incorrect interval')
        parser.print_help()
        exit(-1)
    if args.range_type not in ['days', 'hours']:
        print('error: incorrect range type')
        parser.print_help()
        exit(-1)
    
    create_audit(args.vrops, args.username, args.password, int(args.page_size), exec_timestamp, args.interval_type, args.range_type, int(args.range_count))
