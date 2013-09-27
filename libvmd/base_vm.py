'''
Created on Jul 5, 2013

@author: johnny
'''
import time
import copy
import logging
import re

import vmd_port
import vnc
import databases
import vserver
from utils import ping
import error

NETCARD_DEFAULT = {
    "vnet_type": "Virtio ParaVirtual",
    "pg": "Virtual Machine Network 0",
    "seq": 1
}

VHD_DEFAULT = {
    "vhd_type": "IDE",
    "baseimg": '',
    "del": "no",
    "createvhd": "yes",
    "cache": "none",
    "boot_seq": 1,
    "persistence": "yes",
    "size": 41943040
}

VM_DEFAULT = {
    'hostUuid': '',
    'description': '',
    'bootDevice': 'cdn',
    'storage_path': '',
    'storage_uuid': '',
    'usb_dev_list': [],
    'pcidevice': [],
    'hd': [],
    'memoryAllocatedInMb': '1024',
    'numVcpusAllocated': '1',
    'netcardAllPara': [],
    'usbip': [],
    'cdrom': {},
    'cpu_shares': '1000',
    'autoStart': 'no',
    'soundhw': 'hda',
    'localTime': 'yes',
    'vga': 'std',
    'mouse_type': 'usb',
    "rdpconfig":"open",
}


class VMBase(object):

    def __init__(self, name):
        self.cfg = None
        # Indicate weather the vm is created
        self.host = None
        self.storage = None
        self.settled = False
        self.exe = None
        self.query = None
        self.name = name
        self.vnc_proc = None

    def initialize(self, host):
        self.host = vserver.create_vserver(host)
        self.query = databases.DBQuery(host, user="postgres")

    def add_hd(self, hd=None):
        vhd = copy.deepcopy(VHD_DEFAULT)
        if not hd:
            vhd['baseimg'] = 'no'
        else:
            vhd.update(hd)

        self.cfg['hd'].append(vhd)

    def get_hostname(self):
        return self.host.hostname

    def add_netcard(self, netcard=None):
        ncd = copy.deepcopy(NETCARD_DEFAULT)
        if netcard:
            ncd.update(netcard)

        self.cfg['netcardAllPara'].append(ncd)

#    def get_my_baseimg(self):
#        return self.query.get_vm_baseimg(self.name)

    def get_vhd(self):
        data = self.query.get_vm_vhd(self.name)
        vhds = []
        for vhd in data:
            dd = copy.deepcopy(vmd_port.VHD)
            dd['boot_seq'] = vhd[2]
            dd['vhd_type'] = vhd[3]
            dd['baseimg'] = vhd[4]
            dd['persistence'] = vhd[7]
            dd['cache'] = vhd[8]
            dd['uuid'] = self.get_storage_uuid()
            vhds.append(dd)

    def edit_vhd(self, index, key, value):
        vhd_cfg = self.get_vhd()
        vhd_cfg[index][key] = value

    def edit_netcard(self):
        pass

    def edit_vm(self):
        pass

    def get_storage_path(self):
        return self.query.get_vm_storage("description='%s'" % self.name)

    def get_storage_uuid(self):
        if self.cfg['storage_uuid']:
            return self.cfg['storage_uuid']
        else:
            mount_path = self.get_storage_path()
            return self.query.get_storageUuid("mount_path='%s'" % mount_path)

    def get_vmUuid(self):
        if self.query is not None and self.name is not None:
            keyword = "description='%s'" % self.name
            return self.query.get_vmUuid(keyword)

    def get_parentUuid(self):
        return self.query.get_hostUuid()

    def get_baseimg(self):
        if self.hard_drive['baseimg']:
            return self.hard_drive['baseimg']
        else:
            # Not really logical
            return self.query.get_vm_baseimg(self.name)

    def set_cfg(self, key, value):
        if key in self.cfg.keys():
            self.cfg[key] = value
        else:
            print "Invalid key"

    def verify_vm_ip(self):
        if self.ip:
            temp_list = str(self.ip).split('.')
            if '169' == temp_list[0]:
                raise error.TestError("VM IP not available")

    def is_started(self, has_os=True, timeout=120, err=True):
        """
        has_os: using pre-created img or not, default = True
        timeout: timeout for vm start up, default = 120s
        """
        current = time.time()
        start = time.time()
        endtime = current + timeout

        while current < endtime:
            if has_os:
                self.ip = self.query.get_vm_ip(self.name)
                # IP address verification
                self.verify_vm_ip()
                if ping.ping(self.ip):
                    return time.time() - start
            else:
                try:
                    result = self.host.run(
                    "ps aux|grep fronvmm | grep -v grep").stdout.strip()
                except error.HostRunError:
                    pass

                patt = re.compile(r"-name %s\b" % self.name, re.MULTILINE)
                if result and patt.search(result):
                    return True

            current = time.time()
            time.sleep(1)

        if err:
            raise error.VMStartUpTimeoutError()
        else:
            return False

    def is_down(self, timeout=120, err=True):
        if not self.name:
            return

        current = time.time()
        endtime = current + timeout
        while current < endtime:
            try:
                result = self.host.run(
                "ps aux|grep fronvmm | grep -v grep").stdout.strip()
            except error.HostRunError:
                return True

            patt = re.compile(r"-name %s\b" % self.name, re.MULTILINE)
            if not (result and patt.search(result)):
                return True

            current = time.time()
            time.sleep(2)
        if err:
            raise error.VMShutdownTimeoutError()
        else:
            return False

    def get_vnc_port(self, timeout=30):
        if self.name:
            current = time.time()
            endtime = current + timeout

            while current < endtime:
                port = self.query.get_vnc_port(self.name)
                if port:
                    return port
                current = time.time()
                time.sleep(1)

            raise error.CommonError("Get vm vnc port failed!")

    def start_vnc(self):
        self.vnc_proc = vnc.start_vnc(self.host.hostname,
                                      self.get_vnc_port())

    def close_vnc(self):
        if self.vnc_proc:
            vnc.stop_vnc(self.vnc_proc)
        else:
            logging.info("The vnc process dose not exist")

    def update_cfg(self, cfgs):
        self.cfg.update(cfgs)

    def update_vhd(self, vhd, index=0):
        self.cfg['hd'][index].update(vhd)

    def get_snapshots(self):
        return self.query.get_snapshots(self.name)
