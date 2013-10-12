#!/usr/bin/env python
#-*- coding:utf-8 -*-

LOCAL_IP = '10.10.48.72' #local ip address
ORG_PASSWD = 'daa4b4' #original password of testing host

HOME_PATH = "/var/version_test/"

NODE1 = {
        'name': 'node1',
        'host-name': '48-12',
        'profile': 'vS292b0069-x86_64',
        'interface': 'eth0',
        'mac': '00:E0:81:DE:C9:27',
        'ip': '10.10.48.12',
        'subnet': '255.255.0.0',
        'gateway': '10.10.0.1',
        'name-servers': '219.141.140.10',
        'static': '1',
        'power-type': 'ipmilan',
        'power-user': 'root',
        'power-passwd': 'superuser',
        'power-address': '10.10.48.74'
        }

TEST_CASES = 'stability'
