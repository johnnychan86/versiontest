#-*- coding:utf-8 -*-
'''
Created on 2012-7-11

@author: johnny
'''
import copy
import base_vm


class VMS(base_vm.VMBase):
    def __init__(self, name):
        base_vm.VMBase.__init__(self, name)
        self.cfg = copy.deepcopy(base_vm.VM_DEFAULT)
        self.cfg['description'] = name
        self.name = name
        self.hard_drive = copy.deepcopy(base_vm.VHD_DEFAULT)
        self.netcard = copy.deepcopy(base_vm.NETCARD_DEFAULT)
        
       
    def initialize(self, host, executor):
        super(VMS, self).initialize(host)
        #self.storage = None
        self.exe = executor
        
    def start(self, vnc=True):
        opt_id = 400
        params = {}
        params['parentUuid'] = self.get_parentUuid()
        params['vmUuid'] = self.get_vmUuid()
        params['storage_path'] = self.get_storage_path()
        params['storage_uuid'] = self.get_storage_uuid()
        
        m_id = self.exe.run(opt_id, params, self.host.hostname,
                            'vm', 'VmnoclusterchangeTask')
        self.exe.wait_for_done(m_id, self.host.hostname, 120)
        if vnc:
            self.start_vnc()
    
    def shutdown(self):
        opt_id = 1902
        params = {}
        params['parentUuid'] = self.get_parentUuid()
        params['vmUuid'] = self.get_vmUuid()
        params['storage_path'] = self.get_storage_path()
        
        m_id = self.exe.run(opt_id, params, self.host.hostname,
                     'vm', 'VmnoclusterchangeTask')
        self.exe.wait_for_done(m_id, self.host.hostname, 120)
        
    def restart(self):
        opt_id = 1903
        params = {}
        params['parentUuid'] = self.get_parentUuid()
        params['vmUuid'] = self.get_vmUuid()
        params['storage_path'] = self.get_storage_path()
        
        m_id = self.exe.run(opt_id, params, self.host.hostname,
                     'vm', 'VmnoclusterchangeTask')
        self.exe.wait_for_done(m_id, self.host.hostname, 120)
    
    def poweroff(self):
        opt_id = 401
        params = {}
        params['parentUuid'] = self.get_parentUuid()
        params['vmUuid'] = self.get_vmUuid()
        params['storage_path'] = self.get_storage_path()
        params['storage_uuid'] = self.get_storage_uuid()
        
        m_id = self.exe.run(opt_id, params, self.host.hostname,
                            'vm', 'VmnoclusterchangeTask')
        self.exe.wait_for_done(m_id, self.host.hostname, 120)
    
    def pw_restart(self):
        opt_id = 402
        params = {}
        params['parentUuid'] = self.get_parentUuid()
        params['vmUuid'] = self.get_vmUuid()
        params['storage_path'] = self.get_storage_path()
        
        m_id = self.exe.run(opt_id, params, self.host.hostname,
                     'vm', 'VmnoclusterchangeTask')
        self.exe.wait_for_done(m_id, self.host.hostname, 120)
    
    def pause(self):
        opt_id = 404
        params = {}
        
        params['vmUuid'] = self.get_vmUuid()
        params['parentUuid'] = self.get_parentUuid()
        params['storage_path'] = self.get_storage_path()
        
        m_id = self.exe.run(opt_id, params, self.host.hostname,
                                 'vm', 'VmnoclusterchangeTask')
        self.exe.wait_for_done(m_id, self.host.hostname)

    def tools_mount(self):
        opt_id = 423
        params = {}
        params['vmUuid'] = self.get_vmUuid()
        params['storage_path'] = self.get_storage_path()
        params['parentUuid'] = self.get_parentUuid()
        
        m_id = self.exe.run(opt_id, params, self.host.hostname,
                     'vm', 'VmnoclusterchangeTask')
        self.exe.wait_for_done(m_id, self.host.hostname, 120)

    def tools_umount(self):
        opt_id = 424

        params = {}
        params['vmUuid'] = self.get_vmUuid()
        params['storage_path'] = self.get_storage_path()
        params['parentUuid'] = self.get_parentUuid()
        
        m_id = self.exe.run(opt_id, params, self.host.hostname,
                     'vm', 'VmnoclusterchangeTask')
        self.exe.wait_for_done(m_id, self.host.hostname, 60)

    
    def config_ip(self, ip, mask, gateway, wait=False):
        opt_id = 1905
        
        params = {}
        ipconfig = {
                    'gateway': [gateway,],
                    'ip': [{'netmask': mask, 'address': ip}],
                    }
        params['parentUuid'] = self.get_parentUuid()
        params['vmUuid'] = self.get_vmUuid()
        params['storage_path'] = self.get_storage_path()
        params['vmnetcards'] = [ipconfig,]
        
        m_id = self.exe.run(opt_id, params, self.host.hostname,
                     'vm', 'VmnoclusterchangeTask')
        if wait:
            self.exe.wait_for_done(m_id, self.host.hostname, 120)
        return m_id
            
    def config_dns(self, dns, wait=False):
        opt_id = 1907
        
        params = {}
        
        dnsconfig = {'dns': [dns,]}
        
        params['parentUuid'] = self.get_parentUuid()
        params['vmUuid'] = self.get_vmUuid()
        params['storage_path'] = self.get_storage_path()
        params['vmnetcards'] = [dnsconfig]
        
        m_id = self.exe.run(opt_id, params, self.host.hostname,
                     'vm', 'VmnoclusterchangeTask')
        
        if wait:
            self.exe.wait_for_done(m_id, self.host.hostname, 120)
        return m_id
    
    def config_network(self, ip, mask, gateway, dns, wait=True):
        id2 = self.config_dns(dns)
        id1 = self.config_ip(ip, mask, gateway)
        
        if wait:
            self.exe.wait_for_done(id1, self.host.hostname, 120)
            self.exe.wait_for_done(id2, self.host.hostname, 120)
        return (id1, id2)
        
    def config_hostname(self, name, is_restart="yes", wait=True):
        opt_id = 1911
        
        params = {}
        params['parentUuid'] = self.get_parentUuid()
        params['vmUuid'] = self.get_vmUuid()
        params['storage_path'] = self.get_storage_path()
        params['hostname'] = name
        params['is_restart'] = is_restart
        
        m_id = self.exe.run(opt_id, params, self.host.hostname,
                     'vm', 'VmnoclusterchangeTask')
        
        if wait:
            self.exe.wait_for_done(m_id, self.host.hostname, 120)
            
        return m_id
    
    def join_domain(self, domain, account, password,
                    is_restart='yes', wait=True):
        opt_id = 1912
        
        params = {}
        params['parentUuid'] = self.get_parentUuid()
        params['vmUuid'] = self.get_vmUuid()
        params['storage_path'] = self.get_storage_path()
        params['domain'] = domain
        params['account'] = account
        params['password'] = password
        params['is_restart'] = is_restart
        
        m_id = self.exe.run(opt_id, params, self.host.hostname,
                     'vm', 'VmnoclusterchangeTask')
        
        if wait:
            self.exe.wait_for_done(m_id, self.host.hostname, 120)
            
        return m_id
    
    def quit_domain(self, workgroup, account, password,
                    is_restart='yes', wait=True):
        opt_id = 1913
        
        params = {}
        params['parentUuid'] = self.get_parentUuid()
        params['vmUuid'] = self.get_vmUuid()
        params['storage_path'] = self.get_storage_path()
        params['workgroup'] = workgroup
        params['account'] = account
        params['password'] = password
        params['is_restart'] = is_restart
        
        m_id = self.exe.run(opt_id, params, self.host.hostname,
                     'vm', 'VmnoclusterchangeTask')
        
        if wait:
            self.exe.wait_for_done(m_id, self.host.hostname, 120)
            
        return m_id
    