#-*- coding:utf-8 -*-
'''
Created on 2012-8-28

@author: Johnny
'''
action_code = {'start_vm':       400,
               'poweroff_vm':    401,
               'reboot_vm':      402,
               'vm_pause':       404,
               'snapshot':       408,
               're_snapshot':    409,
               'dele_snapshot':  410,
               'flush_snapshot': 411,
               'backup_vm':      416,
               'recover_backup': 417,
               'delete_backup':  418,
               'clear_snapshot': 428,
               'create_vms':     500,
               'delete_vms':     502,
               'diff_clone':     503,
               'clone_vms':      504,
               'vm2temp':        508,
               'delete_temp':    511,
               'vm_trans':       605,}

VM_EDIT = {
           "vmUuid": "",
           "hostUuid": "",
           "parentUuid": "",
           "storage_uuid": "",
           "storage_path": "",
           "description": "",
           "pcidevice": [],
           "autoStart": "no",
           "memoryAllocatedInMb": 1024,
           "numVcpusAllocated": 2,
           "localTime": "yes",
           "usb_dev_list": [],
           "usbip": [],
           "vga": "std",
           "cdrom": {},
           "cpu_shares": "no_limit",
           "hd": [],
           "soundhw": "hda",
           "bootDevice": "cdn",
           "hd": [],
           "netcardAllPara": [],
           }

VHD = {
       "vhd_type": "IDE",
       "baseimg": '',
       "del": "no",
       "createvhd": "no",
       "cache": "none",
       "boot_seq": 1,
       "persistence": "yes",
       "uuid": ""
       }

CLONE_VMS = {
             "targetVmuuid": "",
             "targetVmdesc": "",
             "pcidevice": [],
             "bsstorage_uuid": "",
             "netcardAllPara": [],
             "to_template": "no",
             "storage_path": "",
             "vmUuid": "",
             "storageUuid": "",
             "bsstorage_path": "",
             "parentUuid": "",
             "copy_level": "high"
            }

TAKE_SNAPSHOT = {
                 "snname":"",
                 "sndesc":"",
                 "parentUuid":"",
                 "storage_uuid":"",
                 "storage_path":"",
                 "vmUuid":"",
                 "vmType":"singleVm"
                 }

RECOVER_SNAPSHOT = {
                    "vmType":"singleVm",
                    "parentUuid":"",
                    "storage_uuid":"",
                    "storage_path":"",
                    "vmUuid":"",
                    "snuuid":""
                    }