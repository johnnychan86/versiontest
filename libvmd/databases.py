#-*- coding:utf-8 -*-
'''
Created on 2012-8-1

@author: johnny
'''
import copy, logging
from utils import db_connector


class DBQuery(object):
    def __init__(self, host, user='postgres', 
                 passwd='', db_name='fronware'):
        self.db = db_connector.DataBaseConnection()
        self.db_type = 'psql'
        self.host = host
        self.user = user
        self.passwd = passwd
        self.db_name = db_name
        self.retry_times = 10
    
    def query(self, table, condition=None, column='*'):
        cmd = 'SELECT %s from %s ' % (column, table)
        
        if condition:
            cmd = cmd + "WHERE %s" % condition
            
        cmd = cmd + ';'
        #logging.debug("FROM QUERY: %s" % cmd) 
        return self.execute(cmd)
    
    def insert(self, table, keys, values):
        command = ("INSERT INTO " + str(table) + " " + 
                  keys + """ VALUES (%s, %s, %s, %s, %s,
                  %s, %s, %s, %s, %s, %s);""")
        if isinstance(values, tuple):
            return self.execute(command, values)
    
    def insert1(self, table, args):
        if isinstance(args, dict):
            keys = tuple(args.keys())
            values = tuple([args[k] for k in keys])
            keys = str(keys).replace("'", '')
        else:
            print "Wrong type"
            return
        command = ("INSERT INTO %s %s VALUES" %
                   (str(table), keys))
        command += '({0});'.format(('%s, ' * len(values))[:-2])
        return self.execute(command, values)
            
    def execute(self, command, parameters=None):
        self.db.connect(self.db_type, self.host, 5432,
                               self.user, self.passwd, self.db_name)
        result = self.db.execute(command, parameters)
        self.db.disconnect()
        return result
    
    def get_storageUuid(self, condition=None):
        column = 'uuid'
        results = self.query('storage', condition, column)
        results = [x[0] for x in results]
        if len(results) > 1:
            return results
        elif len(results) == 1:
            return results[0]
    
    def get_vm_storage(self, condition=None):
        column = 'storage_path'
        results = self.query('vms', condition, column)
        results = [x[0] for x in results]
        if len(results) > 1:
            return results
        elif len(results) == 1:
            return results[0]
    
    def get_vm_baseimg(self, vm_name):
        table = "vms a, vms_img b"
        column = "baseimg"
        condition = "a.id=b.vm_id and a.description='%s'" % vm_name
#        command = """SELECT baseimg from vms a, vms_img b
#                  where a.id=b.vm_id and a.description=
#                  '%s'""" % vm_name
        #result = self.execute(command)
        result = self.query(table, condition, column)
        if result:
            arr = [x[0] for x in result]
            if len(arr):
                return arr[0]
        else:
            return None
    
    def get_vm_vhd(self, vm_name):
        table = "vms a, vms_img b"
        column = "b.*"
        condition = "a.id=b.vm_id and a.description='%s'" % vm_name
#        command = """SELECT b.* from vms a, vms_img b
#                  where a.id=b.vm_id and a.description=
#                  '%s'""" % vm_name
#        result = self.execute(command)
        result = self.query(table, condition, column)
        return result
    
    def get_storagepath(self, keyword=None):
        column = 'mount_path'
        results = self.query('storage', keyword, column)
        results = [x[0] for x in results]
        if len(results) > 1:
            return results
        elif len(results) == 1:
            return results[0]
    
    def get_hostUuid(self):
        column = 'uuid'
        results = self.query('hosts', '', column)
        results = [x[0] for x in results]
        if len(results) > 1:
            return results
        elif len(results) == 1:
            return results[0]
    
    def get_vmUuid(self, keyword=None):
        column = 'uuid'
        results = []
        times = 0       
        while not results and times < self.retry_times:
            results = self.query('vms', keyword, column)
            times += 1
        
        results = [x[0] for x in results]
        if len(results) > 1:
            return results
        elif len(results) == 1:
            return results[0]
    
    def get_vms_list(self):
        column = 'description'
        results = self.query('vms', column=column)
        results = [x[0] for x in results]
        if len(results) >= 1:
            return results
        
    def get_vnc_port(self, vm):
        column = 'vnc_port'
        keyword = "description=\'" + vm + "\'"
        results = self.query('vms', keyword, column)
        results = [x[0] for x in results]
        if len(results) > 1:
            return results
        elif len(results) == 1:
            return results[0]
        
    def get_vm_ip(self, vm):
        table = "vms a, netcard_vms b, netcard_vms_ip c"
        column = "ip"
        condition = "a.id=b.vm_id and b.id=c.vnet_id and a.description='%s'" % vm
        result = self.query(table, condition, column)
        if result:
            arr = [x[0] for x in result]
            if len(arr):
                return arr[0]
        else:
            return 0
    
    def get_mission_stat(self, mid):
        column = 'task_execute_stat'
        keyword = "id=%s" % str(mid)
        results = self.query('missions', keyword, column)
        if results:
            arr = [x[0] for x in results]
            if len(arr):
                return arr[0]
        else:
            return 0
    
    def get_mission_message(self, mid):
        column = 'message'
        keyword = "id=%s" % str(mid)
        results = self.query('missions', keyword, column)
        if results:
            arr = [x[0] for x in results]
            if len(arr):
                return arr[0]
        else:
            return 0
        
    def get_mission_id_max(self, keyword=None):
        column = 'max(id)'
        results = self.query('missions', keyword, column)
        if results:
            arr = [x[0] for x in results]
            if len(arr):
                return arr[0]
        else:
            return 0
        
    def get_mission_id_min(self, keyword=None):
        column = 'min(id)'
        results = self.query('missions', keyword, column)
        if results:
            arr = [x[0] for x in results]
            if len(arr):
                return arr[0]
        else:
            return None
    
    def get_vmtype(self, vm):
        #TODO
        pass

    def get_vm_name(self, uuid):
        column = 'description'
        keyword = "uuid='%s'" % uuid

        result = self.query('vms', keyword, column)
        if result:
            arr = [x[0] for x in result]
            if len(arr):
                return arr[0]
        else:
            return None
    
    def get_backup_storagepath(self, backup_id):
        table = 'vmbackups, storage'
        column = 'storage.mount_path'
        condition = "vmbackups.id='%s'and vmbackups.storage_id=storage.id" % backup_id
        
        result = self.query(table, condition, column)
        if result:
            arr = [x[0] for x in result]
            if len(arr):
                return arr[0]
        else:
            return 0
    
    def get_backup_storageuuid(self, backup_id):
        table = 'vmbackups, storage'
        column = 'storage.uuid'
        condition = "vmbackups.id='%s'and vmbackups.storage_id=storage.id" % backup_id
        
        result = self.query(table, condition, column)
        if result:
            arr = [x[0] for x in result]
            if len(arr):
                return arr[0]
        else:
            return 0
    
    def get_backup_info(self, backup_id):
        info = {}
        table = 'vmbackups'
        condition = "id='%s'" % backup_id
        
        result = self.query(table, condition)
        if result:
            result = result[0]
            keys = ('id', 'vm_uuid', 'vm_desc', 'baknum', 'bakdsc',
                    'baktim', 'baktype', 'totalsize', 'storage_id')
            info.update(zip(keys, result))
            info['storage_path'] = self.get_backup_storagepath(backup_id)
            info['storage_uuid'] = self.get_backup_storageuuid(backup_id)
            return info
        else:
            return 0
        
    def get_backups(self, vm_uuid, numb=None):
        table = 'vmbackups'
        column = 'id'
        if numb:
            condition = "vm_uuid='%s' and baknum=%s" % (vm_uuid, str(numb))
        else:
            condition = "vm_uuid='%s'" % vm_uuid
        
        result = self.query(table, condition, column)
        if result:
            arr = [x[0] for x in result]
            if len(arr):
                return arr
        else:
            return 0
    
    def get_snapshots(self, vm_name):
        table = "snapshots a, vms b"
        column = "a.uuid"
        condition = "b.id=a.vm_id and b.description='%s'" % vm_name
#        command = """SELECT a.uuid from snapshots a, vms b
#         where b.id=a.vm_id and b.description='%s';""" % vm_name
#         
#        result = self.execute(command)
        result = self.query(table, condition, column)
        if result:
            arr = [x[0] for x in result]
            if len(arr):
                return arr
        else:
            return 0
        
    def is_current_snapshot(self, snapuuid):
        table = "snapshots"
        column = "parent_uuid"
        condition = "description='You Are Here'"
#        command = """SELECT parent_uuid from
#        snapshots where description='You Are Here';""" 
         
        #result = self.execute(command)
        result = self.query(table, condition, column)
        
        if result:
            arr = [x[0] for x in result]
            if snapuuid in arr:
                return True
            
            column = "description"
            condition = "uuid='%s'" % snapuuid

            result = self.query(table, condition, column)
            if result:
                arr = [x[0] for x in result]
                if len(arr):
                    arr = arr[0]
                if arr == 'You Are Here' or arr == 'rootsnap':
                    return True
                else:
                    return False
        
    