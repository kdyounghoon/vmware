# -*- coding: utf-8 -*-
'''
  ____  ___   ____________  ___  ___  ____     _________________
 / __ \/ _ | / __/  _/ __/ / _ \/ _ \/ __ \__ / / __/ ___/_  __/
/ /_/ / __ |_\ \_/ /_\ \  / ___/ , _/ /_/ / // / _// /__  / /   
\____/_/ |_/___/___/___/ /_/  /_/|_|\____/\___/___/\___/ /_/    
         Operational Aid Source for Infra-Structure 

Created on 2021. 3. 18..
@author: Hye-Churn Jang, CMBU Specialist in Korea, VMware [jangh@vmware.com]
'''

from vra import VRA, pp

o_vra_desc = {
    'base_url': 'https://###.com',
    'username': '###',
    'password': '###'
}

n_vra_desc = {
    'base_url': 'https://####.com',
    'username': '###',
    'password': '###!'
}

o_vra = VRA(**o_vra_desc)
n_vra = VRA(**n_vra_desc)

#===============================================================================
# Delete All IP Addresses on New VRA
#===============================================================================
print('Delete All IP Addresses on New VRA ----------------------------------->')
n_ip_addrs = n_vra.get('/provisioning/uerp/resources/ip-addresses?expand&$top=10000')
n_ip_addrs.raise_for_status()
n_ip_addrs = n_ip_addrs.json()
count = 0
for n_ip_addr_link, n_ip_addr in n_ip_addrs['documents'].items():
    try:
        n_intf = n_vra.get('/provisioning/uerp' + n_ip_addr['connectedResourceLink'])
        if 'address' in n_intf: n_intf.pop('address')
        if 'addressLinks' in n_intf: n_intf['addressLinks'] = []
        n_vra.patch('/provisioning/uerp' + n_ip_addr['connectedResourceLink'], n_intf)
    except: pass
    
    try: n_vra.delete('/provisioning/uerp' + n_ip_addr_link).raise_for_status()
    except Exception as e:
        print('! could not delete ip address : {}'.format(str(e)))
        try: pp(n_vra.get('/provisioning/uerp' + n_ip_addr_link).json())
        except: pass
    else:
        count += 1
        print('[{}] delete ip address : {}'.format(count, n_ip_addr_link))
print('(OK) {}\n\n'.format(count))
# input('press enter to next')

#===============================================================================
# Delete All Subnet Range on New VRA
#===============================================================================
print('Delete All Subnet Ranges on New VRA ---------------------------------->')
n_ranges = n_vra.get('/provisioning/uerp/resources/subnet-ranges?$top=10000')
n_ranges.raise_for_status()
n_ranges = n_ranges.json()
count = 0
for n_range_link in n_ranges['documentLinks']:
    try: n_vra.delete('/provisioning/uerp' + n_range_link).raise_for_status()
    except Exception as e:
        print('! could not delete range : {}'.format(str(e)))
        try: pp(n_vra.get('/provisioning/uerp' + n_range_link).json())
        except: pass
    else:
        count += 1
        print('[{}] delete range : {}'.format(count, n_range_link))
print('(OK) {}\n\n'.format(count))

#===============================================================================
# Get All Subnets
#===============================================================================
print('Get All Subnets ------------------------------------------------------>')
print('  Get Old Subnets : ', end='')
o_subnets = o_vra.get('/provisioning/uerp/resources/sub-networks?expand&$top=10000')
o_subnets.raise_for_status()
o_subnets = o_subnets.json()
print(o_subnets['documentCount'])
o_subnets = o_subnets['documents']
print('  Get New Subnets : ', end='')
n_subnets = n_vra.get('/provisioning/uerp/resources/sub-networks?expand&$top=10000')
n_subnets.raise_for_status()
n_subnets = n_subnets.json()
print(n_subnets['documentCount'])
n_subnets = n_subnets['documents']
print('(OK)\n\n')

#===============================================================================
# Get Old Subnet Ranges
#===============================================================================
print('Get Old Subnet Ranges ------------------------------------------------>')
o_ranges = o_vra.get('/provisioning/uerp/resources/subnet-ranges?expand&$top=10000')
o_ranges.raise_for_status()
o_ranges = o_ranges.json()
old_count = o_ranges['documentCount']
print('(OK) {}\n\n'.format(old_count))
o_ranges = o_ranges['documents']

#===============================================================================
# Sync All Subnet Ranges
#===============================================================================
print('Sync All Subnet Ranges ----------------------------------------------->')
count = 0
for o_range in o_ranges.values():
    o_subnet = o_subnets[o_range['subnetLink']]
    for n_subnet in n_subnets.values():
        if o_subnet['id'] == n_subnet['id'] and o_subnet['name'] == n_subnet['name']:
            n_range = {
                'name': o_range['name'],
                'fabricNetworkId': n_subnet['documentSelfLink'].split('/sub-networks/')[1],
                'ipVersion': o_range['ipVersion'],
                'startIPAddress': o_range['startIPAddress'],
                'endIPAddress': o_range['endIPAddress']
            }
            if 'description' in o_range: n_range['description'] = o_range['description']
            try: n_vra.post('/iaas/api/network-ip-ranges', n_range).raise_for_status();
            except Exception as e:
                print('! could not create range : {}'.format(str(e)))
                pp(n_range)
            else:
                count += 1
                print('[{}] create range : {} [ {} ]'.format(count, n_subnet['name'], o_range['name']))
            break
print('(OK) New:{} / Old:{}\n\n'.format(count, old_count))

#===============================================================================
# Get New Subnet Ranges
#===============================================================================
print('Get New Subnet Ranges ------------------------------------------------>')
n_ranges = n_vra.get('/provisioning/uerp/resources/subnet-ranges?expand&$top=10000')
n_ranges.raise_for_status()
n_ranges = n_ranges.json()
count = n_ranges['documentCount']
n_ranges = n_ranges['documents']
for n_range in n_ranges.values():
    n_subnet = n_subnets[n_range['subnetLink']]
    if 'rangeLinks' not in n_subnet: n_subnet['rangeLinks'] = []
    n_subnet['rangeLinks'].append(n_range['documentSelfLink'])
print('(OK) {}\n\n'.format(count))
            
#===============================================================================
# Get Old Allocated IP Addresses
#===============================================================================
print('Get Old Allocated IP Addresses --------------------------------------->')
o_ip_addrs = o_vra.get('/provisioning/uerp/resources/ip-addresses?$top=10000')
o_ip_addrs.raise_for_status()
o_ip_addrs = o_ip_addrs.json()
old_all_count = o_ip_addrs['documentCount']
o_ip_addrs = o_vra.get("/provisioning/uerp/resources/ip-addresses?expand&$top=10000&$filter=(ipAddressStatus eq 'ALLOCATED')")
o_ip_addrs.raise_for_status()
o_ip_addrs = o_ip_addrs.json()
old_alloc_count = o_ip_addrs['documentCount']
print('(OK) Allocated:{} / AllStatus:{}\n\n'.format(old_alloc_count, old_all_count))
o_ip_addrs = o_ip_addrs['documents']

#===============================================================================
# Get Old Subnet Ranges
#===============================================================================
print('Get Old Network Interfaces ------------------------------------------->')
o_intfs = o_vra.get('/provisioning/uerp/resources/network-interfaces?expand&$top=10000')
o_intfs.raise_for_status()
o_intfs = o_intfs.json()
old_count = o_intfs['documentCount']
print('(OK) {}\n\n'.format(old_count))
o_intfs = o_intfs['documents']

#===============================================================================
# Sync All IP Addresses
#===============================================================================
print('Sync All IP Addresses ------------------------------------------------>')
alloc_count = 0
dummy_count = 0
error_count = 0
total_count = 0
count = 0
for o_ip_addr in o_ip_addrs.values():
    count += 1
    ip_address = o_ip_addr['ipAddress']
    o_range = o_ranges[o_ip_addr['subnetRangeLink']]
    o_subnet = o_subnets[o_range['subnetLink']]
    try: o_intf_id = o_intfs[o_ip_addr['connectedResourceLink']]['id']
    except Exception as e:
        print('! {} could not find network interface on old, ip will be allocated on dummy interface : {}'.format(ip_address, str(e)))
        n_intf_link = 'dummy'
    else:
        n_intfs = n_vra.get("/provisioning/uerp/resources/network-interfaces?expand&$filter=(id eq '{}')".format(o_intf_id)).json()
        if n_intfs['documentCount'] == 1:
            n_intf_link = n_intfs['documentLinks'][0]
            n_intf = n_intfs['documents'][n_intf_link]
        elif n_intfs['documentCount'] > 1:
            print('! {} network interface ids are duplicated on new, ip will be allocated on dummy interface'.format(ip_address))
            pp(n_intfs['documentLinks'])
            n_intf_link = 'dummy'
        else:
            print('! {} could not find network interfaces on new, ip will be allocated on dummy interface'.format(ip_address))
            n_intf_link = 'dummy'
    for n_subnet in n_subnets.values():
        if o_subnet['id'] == n_subnet['id'] and o_subnet['name'] == n_subnet['name']:
            for n_range_link in n_subnet['rangeLinks']:
                n_range = n_ranges[n_range_link]
                if o_range['name'] == n_range['name']:
                    n_ip_addr = {
                        'customProperties': {},
                        'ipAddress': ip_address,
                        'ipAddressStatus': 'ALLOCATED',
                        'subnetRangeLink': n_range['documentSelfLink'],
                        'connectedResourceLink': n_intf_link
                    }
                    try: n_ip_addr = n_vra.post('/provisioning/uerp/resources/ip-addresses', n_ip_addr).json()
                    except Exception as e:
                        print('! {} could not create ip address allocation, it might will be done at next subnet range : {}'.format(ip_address, str(e)))
                        pp(n_ip_addr)
                    else:
                        if n_intf_link == 'dummy': dummy_count += 1
                        else:
                            alloc_count += 1
                            n_intf['address'] = ip_address
                            if 'addressLinks' not in n_intf: n_intf['addressLinks'] = []
                            n_intf['addressLinks'].append(n_ip_addr['documentSelfLink'])
                            try: n_vra.patch('/provisioning/uerp' + n_intf_link, n_intf)
                            except: pass
                        total_count += 1
                        print('[(A{}-D{}-E{}) {} / {}] {} create ip address allocation'.format(alloc_count, dummy_count, error_count, total_count, count, ip_address))
                        break
            else:
                error_count += 1
                print('[(A{}-D{}-E{}) {} / {}] {} could not create ip address allocation by matching ranges'.format(alloc_count, dummy_count, error_count, total_count, count, ip_address))
            break
    else:
        error_count += 1
        print('[(A{}-D{}-E{}) {} / {}] {} could not create ip address allocation by matching subnets'.format(alloc_count, dummy_count, error_count, total_count, count, ip_address))
print('(OK) New:{} / Old:{}\n\n'.format(count, old_alloc_count))







