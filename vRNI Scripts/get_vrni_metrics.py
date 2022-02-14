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
    "username": "admin@local",
    "password": "VMware1!",
    "domain": {
        "domain_type": "LOCAL"
        }
    }

    resp = requests.post(
        base_url + '/api/ni/auth/token',
        headers=headers, json=data,
        verify=False)
    resp.raise_for_status()


    headers['Authorization'] = 'NetworkInsight ' + resp.json()['token']
    print("### Logged into vrni: " + vrni_url)

    wr.writerow(["Entity Type", "metric", "display_name", "intervals", "description"])

    entity_types = [
        "VirtualMachine",
        "Host",
        "Vnic",
        "Vmknic",
        "VxlanLayer2Network",
        "VlanL2Network",
        "Cluster",
        "SecurityTag",
        "ResourcePool",
        "NSXIPSet",
        "EC2IPSet",
        "NSXTIPSet",
        "NSXSecurityGroup",
        "EC2SecurityGroup",
        "NSGroup",
        "Flow",
        "ProblemEvent",
        "Application",
        "Tier",
        "IPEndpoint",
        "NSXFirewallRule",
        "EC2SGFirewallRule",
        "NSXRedirectRule",
        "VCenterManager",
        "NSXVManager",
        "NSXTManager",
        "NSXPolicyManager",
        "NSXService",
        "EC2Service",
        "NSService",
        "VPC",
        "NSXDistributedFirewall",
        "EC2Firewall",
        "NSXServiceGroup",
        "NSServiceGroup",
        "DistributedVirtualSwitch",
        "DistributedVirtualPortgroup",
        "VCDatacenter",
        "Datastore",
        "Folder",
        "NSXTFirewallRule",
        "NSXTFirewall",
        "CheckpointFirewall",
        "CheckpointFirewallRule",
        "KubernetesService",
        "CheckpointManager",
        "CheckpointMDSManager",
        "AzureNSGRule",
        "AzureASG",
        "AzureNSG",
        "AzureVM",
        "CloudNetwork",
        "FirewallRuleMaskEvent",
        "NSXPolicyGroup",
        "PolicyManagerFirewall",
        "PolicyManagerFirewallRule",
        "UserDefinedProblemEvent",
        "EdgeDevice",
        "RouterDevice",
        "NSXController",
        "LogicalRouter",
        "NSXTManagementNode",
        "NSXTController",
        "NSXTTransportNode",
        "NSXTTransportZone",
        "NSXTLoadBalancer",
        "NSXTVirtualServer",
        "NSXTServerPool",
        "NSXTLogicalSwitch",
        "NSXTRouterDevice",
        "NSXTEdgeCluster",
        "NSXControllerCluster"
    ]



    for entity_type in entity_types:


        print("------- Getting metrics for: " + entity_type + " -------")

        resp = requests.get(
        base_url + '/api/ni/schema/' + entity_type + '/metrics',
        headers=headers,
        verify=False)

        if 'results' in resp.json():
            metrics = resp.json()['results']
        else:
            print("------> There is no metrics for " + entity_type)

        for metric in metrics:
        
            array = []

            array.append(entity_type)

            array.append(metric['metric'])

            array.append(metric['display_name'])

            array.append(metric['intervals'])

            array.append(metric['description'])

            wr.writerow(array)

            print("#### done writing for " + entity_type)
  


 
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--hostname', default='192.168.110.221', help='vRealize Network Insight')
    parser.add_argument('-U', '--username', default='admin@local', help='vRealize Network Insight Admin Username')
    parser.add_argument('-P', '--password', default='VMware1!', help='Network Insight Admin Password')
    parser.add_argument('-F', '--filename', default='vrni-metrics', help='filename')

    args = parser.parse_args()

    get_vrni_metrics(args.hostname, args.username, args.password, args.filename)