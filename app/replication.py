import argparse
import requests
import base64
#from tabulate import tabulate
import xml.etree.ElementTree as ET
from datetime import datetime
import csv
import getpass


def session_auth(username, password, api_url, org):
    b64_en = "Basic " + str(base64.b64encode(str(username) + "@" + str(org) + ":" + str(password)))
    url = api_url + '/api/sessions'
    headers = {'Accept': 'application/*+xml;version=5.6', 'Authorization': b64_en}
    r = requests.post(url, headers=headers)
    if r.status_code != 200:
        return None, None
    xml_aux = ET.fromstring(r.content)
    api_url = xml_aux.attrib['href'].rsplit('/', 2)[0]
    return r.headers['x-vcloud-authorization'], api_url


def get_org(authtoken, api_url, org):
    url = api_url + '/api/org'
    headers = {'Accept': 'application/*+xml;version=5.6', 'x-vcloud-authorization': authtoken}
    r = requests.get(url, headers=headers)
    xml_aux = ET.fromstring(r.content)
    for child in xml_aux:
        if 'application/vnd.vmware.vcloud.org+xml' in child.attrib['type'] and child.attrib['name'] == org:
            return child.attrib['name'], child.attrib['href']

    print "no org found"
    return


# get list of VM name / replication_id
def get_replications(authtoken, org1):
    i = 1
    replicas = []
    vm_cgid = []
    #vm_cgid.append(['vm_name', 'replication_href', 'replicationState', 'RPO(Hours)', 'RPO violation',
    #                'HTTP status_code', 'TransferStartTime', 'TransferSeconds', 'TransferBytes'])
    headers = {'Accept': 'application/*+xml;version=5.6', 'x-vcloud-authorization': authtoken}

    while (True):
        #print i
        url = org1 + '/replications?pageSize=128&page='+str(i)
        r = requests.get(url, headers=headers)
        xml_aux = ET.fromstring(r.content)
        if (len(xml_aux) == 1):
            #print ('exiting...')
            break
        for child in xml_aux:
            if 'application/vnd.vmware.hcs.replicationGroup+xml' in child.attrib['type']:
                replicas.append(child.attrib['href'])
        i += 1

    for href in replicas:
        print href
        r1 = requests.get(href, headers=headers)
        xml_2 = ET.fromstring(r1.content)
        replication_state = 'None'
        transfer_start_time = 'None'
        transfer_seconds = 'None'
        transfer_bytes = 'None'
        rpo = 'None'
        rpoviolation = 'None'

        if 'name' in xml_2.attrib.keys():
            name = xml_2.attrib['name']
        else:
            name = 'no_name'
        for child in xml_2:
            if 'ReplicationState' in child.tag:
                replication_state = child.text
            if child.tag.endswith('Rpo'):
                rpo = float(child.text)/60
            if 'ReplicationGroupInstance' in child.tag:
                for rep_group in child:
                    if 'TransferStartTime' in rep_group.tag:
                        transfer_start_time = rep_group.text
                        if (datetime.utcnow() - datetime.strptime(transfer_start_time, "%Y-%m-%dT%H:%M:%S.%fZ"))\
                                .total_seconds()/3600.0 > rpo:
                            rpoviolation = 'TRUE'
                        else:
                            rpoviolation = 'FALSE'
                    if 'TransferSeconds' in rep_group.tag:
                        transfer_seconds = rep_group.text
                    if 'TransferBytes' in rep_group.tag:
                        transfer_bytes = rep_group.text
        vm_cgid.append([name, href, replication_state, rpo, rpoviolation, r1.status_code, transfer_start_time,
                        transfer_seconds, transfer_bytes])
    return vm_cgid


def replications(username, password, url, org):
    user = username
    api_url = 'https://' + url + '-vcd.vchs.vmware.com'
    password = password
    org = org
    #outfile = args.f

    authtoken, api_url = session_auth(user, password, api_url, org)
    if authtoken is None or api_url  is None:
        exit('cannot authenticate for user %s to org %s' % (user.upper(), org.upper()))
    #print authtoken

    (org_name, org1) = get_org(authtoken, api_url, org)
    org_id = org1.split('/')[-1]

    #print "getting all replicas... May take a while..."
    replicas = get_replications(authtoken, org1)
    # print tabulate(replicas, tablefmt="grid", headers=["VM_Name", "replication_HREF", 'status', rpo,
    # 'http_code', 'TransferStartTime', 'TransferSeconds', 'TransferBytes'])
    #print "export csv..."
    #with open(outfile, 'wb') as csv_file:
    #    writer = csv.writer(csv_file)
    #    for i in replicas:
    #        print i
    #        writer.writerow(i)
    return replicas
