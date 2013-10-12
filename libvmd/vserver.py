'''
Created on Sep 14, 2012

@author: johnny
'''

import time
import cmd, storage
import vmi as vm
from hosts import ssh_host
from databases import DBQuery
import error


class VServer(ssh_host.SSHHost):
    '''
    classdocs
    '''
    
    def _initialize(self, hostname, *args, **dargs):
        super(VServer, self)._initialize(hostname=hostname, *args, **dargs)
        self.db_query = DBQuery(self.hostname)
        self.uuid = self.db_query.get_hostUuid()
        self.exe = cmd.Executer()
    
    def get_system_time(self, f="%FT%T"):
        command = "date +\"%s\"" % f
        try:
            time_str = self.run(command)
        except Exception:
            print Exception
        else:
            return time_str.stdout.strip()
            
        
        
    def add_storage(self, name, storage_type, par, is_mount=True, timeout=300):
        opt_id = 200
        params = {}
        params['hostUuid'] = self.uuid
        params['isMount'] = 'yes' if is_mount else 'no'
        params['storageName'] = name
        params['storageType'] = storage_type
        params['storagePar'] = par
        
        m_id = self.exe.run(opt_id, params, self.hostname, 'storage', 'StorageTask')
        self.exe.wait_for_done(m_id, self.hostname, timeout)
    
    def add_storage_iscsi(self, name, disk, ip, format=True, timeout=300):
        disk_info = self.get_iscsi_service(disk, ip)
        par = {"fileSystem": "yes" if format else "no", 
               "wwid": disk_info['wwid']}
        
        self.add_storage(name, 'iSCSI', par, timeout)
        
    
    def discover_iscsi(self, ip, port=3260, timeout=180):
        opt_id = 220
        params = {
                  'ip': ip,
                  'discovery_password': "",
                  'discovery_username': "",
                  'discovery_username_in': "",
                  'discovery_password_in': "",
                  'hostUuid': self.uuid,
                  'port': str(port)
                  }
        
        m_id = self.exe.run(opt_id, params, self.hostname, 'storage', 'StorageTask')
        self.exe.wait_for_done(m_id, self.hostname, timeout)
    
    def iscsi_auth(self, disk, ip, user, passwd, timeout=180):
        opt_id = 221
        disk_info = self.get_iscsi_service(disk, ip)
        params = {
                  'hostUuid': self.uuid,
                  'target': disk_info['servicename'],
                  'ipport': disk_info['serviceipport'],
                  'account': {"password_in": "",
                              "password": passwd,
                              "authmethod": "CHAP",
                              "username": user,
                              "username_in":""}
                  }
        m_id = self.exe.run(opt_id, params, self.hostname, 'storage', 'StorageTask')
        self.exe.wait_for_done(m_id, self.hostname, timeout)
    
    def is_mounted(self, storage_name, timeout=120):
        current = time.time()
        endtime = current + timeout
        path = storage.get_storage_path(self.hostname, storage_name)
        
        if not path:
            raise error.TestError("Database query failed, storage dose not exist: %s"
                                  % storage_name)
        
        while current < endtime:
            mountlist = self.run("mount").stdout.strip()
            if mountlist.find(path) >= 0:
                return True
            current = time.time()
            time.sleep(2)
            
        raise error.TestError("Mount storage Failed: %s" % storage_name)   
        
    def del_storage(self, name):
        opt_id = 201
        storage_uuid = storage.get_storage_uuid(self.hostname, name)
        params = {}
        params.update({'storageUuid': storage_uuid})
        
        m_id = self.exe.run(opt_id, params, self.hostname, 'storage', 'StorageTask')
        self.exe.wait_for_done(m_id, self.hostname)
        
    def is_storage_deleted(self, storage_name, timeout):
        current = time.time()
        endtime = current + timeout
        path = storage.get_storage_path(self.hostname, storage_name)
        
        if path:
            raise error.TestError("Storage info is not deleted from database: %s"
                                  % storage_name)
            
        while current < endtime:
            mountlist = self.run("mount").stdout.strip()
            if mountlist.find(storage_name) < 0:
                return True
            current = time.time()
            time.sleep(2)
            
        raise error.TestError("Delete storage Failed: %s" % storage_name)
    
    def get_exist_vm(self, vm_name=None):
        if vm_name:
            m_vm = vm.VMS(vm_name)
            m_vm.initialize(self.hostname, self.exe)
            return m_vm
        
        vm_list = []
        vm_names = self.db_query.get_vms_list()
        for name in vm_names:
            m_vm = vm.VMS(name)
            m_vm.initialize(self.hostname, self.exe)
            vm_list.append(m_vm)
            
        return vm_list

    def get_vm_by_uuid(self, uuid):
        vmname = self.db_query.get_vm_name(uuid)
        m_vm = vm.VMS(vmname)
        m_vm.initialize(self.hostname, self.exe)
        return m_vm
    
    def get_storage_path(self, storage_name):
        return self.db_query.get_storagepath("description='%s'" %
                                             storage_name)
    def get_storage_uuid(self, storage_name):
        return self.db_query.get_storageUuid("description='%s'" %
                                              storage_name)
        
    def get_iscsi_service(self, disk, ip):
        result = self.db_query.get_iscsi_service(disk, ip)
        result = {
                  'serviceipport': result[0],
                  'servicename': result[1],
                  'wwid': result[2]
                  }
        return result

    def get_backup_info(self, backup_id):
        return self.db_query.get_backup_info(backup_id)
    
    def get_backups(self, vm_uuid, backup_numb):
        return self.db_query.get_backups(vm_uuid, backup_numb)
    
    def capture_sys_log(self):
        pass
    
    def config_network_bat(self, vms, baseip, mask, gateway, dns, para=False):
        if isinstance(vms, list):
            vm_lst = [self.get_exist_vm(vm) for vm in vms]
            
            base = [int(i) for i in baseip.split('.')]
            ips = []
            base[3] -= 1
            
            for x in range(len(vm_lst)):
                if base[3] < 254:
                    base[3] += 1
                else:
                    base[2] += 1
                    base[3] = 1
                ips.append([str(s) for s in base])
            
            ips = ['.'.join(x) for x in ips]
            
            missions = []
            for cf in zip(vm_lst, ips):
                ids = cf[0].config_network(cf[1], mask, gateway,
                                           dns, wait=(not para))
                missions.extend(ids)
            
            if para:
                for i in missions:
                    self.exe.wait_for_done(i, self.hostname)
        else:
            return False
                
    def config_hostname_bat(self, vms, basename, parallel=False):
        if isinstance(vms, list):
            vm_lst = [self.get_exist_vm(vm) for vm in vms]
            names = [basename + '-' + str(i) for i in range(len(vm_lst))]
            
            missions = []
            for cf in zip(vm_lst, names):
                m_id = cf[0].config_hostname(cf[1], wait=(not parallel))
                missions.append(m_id)
                
            if parallel:
                for i in missions:
                    self.exe.wait_for_done(i, self.hostname)
                
        else:
            return False
        
    def copy_file(self, source, dest, keep_src="yes", cover="yes"):
        opt_id = 212
        params = {}
        
        params['hostUuid'] = self.uuid
        params['src_path'] = source
        params['dst_path'] = dest
        params['keep_source'] = keep_src
        params['cover'] = cover
        
        start = time.time()
        m_id = self.exe.run(opt_id, params, self.hostname, 'storage', 'StorageTask')
        self.exe.wait_for_done(m_id, self.hostname, timeout=1800)
        end = time.time()
        
        print "vserver.copy_file: this action takes %ss" % str(end - start)
    
    def file_exist(self, path, timeout=60):
        current = time.time()
        endtime = current + timeout
        
        while current < endtime:
            command = "[ -f %s ] && echo \"File exists\" || echo \"File does not exists\"" % path
            result = self.run(command).stdout.strip()
            print result
            if result == "File exists":
                return True
            
            current = time.time()
            time.sleep(2)
            
        raise error.TestError("File dose not exist: %s" % path)   


def create_vserver(hostname, **args):
    """
    factory function, return an vserver instance
    The same as host.factory, but maybe more further
    """
    
    classes = [VServer]

    # create a custom host class for this machine and return an instance of it
    host_class = type("%s_host" % hostname, tuple(classes), {})
    host_instance = host_class(hostname, **args)

    return host_instance
