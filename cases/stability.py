'''
Created on Jun 4, 2013

@author: johnny
'''
import unittest, time, logging, random
from libvmd import cmd, vserver, storage
from libvmd import databases
import const

HOST = const.NODE1['ip']

class Test(unittest.TestCase):


    def setUp(self):
        self.vserver = vserver.create_vserver(HOST)
        self.handler = cmd.Manager()
        self.query = databases.DBQuery(HOST)

    def logging_info(self, info):
        logging.info(">> %s(%s: %s)" % 
        (info, HOST, self.vserver.get_system_time()))

    def tearDown(self):
        system_time = "QUIT TIME(%s): %s" % \
                      (HOST, self.vserver.get_system_time()) 
        logging.info(system_time)

    def mount_storage(self):
        self.logging_info('mount_storage')
        
        self.cifs = storage.CIFS_DEFAULT
        self.cifs['serviceip'] = '10.10.1.40'
        self.cifs['resource'] = 'cifs/chenximing'
        self.cifs['username'] = 'admin'
        self.cifs['password'] = '111111'
        self.nfs = {'serviceip': '10.10.1.40',
                    'resource': '/mnt/test/nfs/chenximing'
                    }
        
        self.vserver.add_storage('autoadd_cifs', 'CIFS', self.cifs)
        self.vserver.is_mounted('autoadd_cifs', timeout=300)
        self.vserver.add_storage('autoadd_nfs', 'NFS', self.nfs)
        self.vserver.is_mounted('autoadd_nfs', timeout=300)

        self.vserver.discover_iscsi('10.10.1.40')
        self.vserver.iscsi_auth('disk5', '10.10.1.40', 'chenximin', '111111')
        self.vserver.add_storage_iscsi('autoadd_iscsi', 'disk5', '10.10.1.40')
        self.vserver.is_mounted('autoadd_iscsi', timeout=300)
        
    def copy_img(self):
        self.logging_info('copy_img')
        
        des = self.vserver.get_storage_path('defaultlocal')
        src = self.vserver.get_storage_path('autoadd_cifs') + '/imgs/winxp-tools-auto.img'
        self.vserver.copy_file(src, des)
        self.vserver.file_exist(des + "/winxp-tools-auto.img")
        
    def create_vm(self, name):
        self.logging_info('create_vm')
        
        self.img = self.handler.get_img_path(HOST, 'defaultlocal', 'winxp-tools-auto.img')
        
        vm = self.handler.create(name, HOST, img=self.img)
        
        vm.start(vnc=False)
        vm.is_started(has_os=False, timeout=300)
        time.sleep(5)
        vm.poweroff()
        vm.is_down(200)
        return vm
    
    def tools_install(self, vm):
        self.logging_info('tools_install')
        
        vm.start(vnc=False)
        vm.is_started(has_os=False, timeout=300)
        time.sleep(5)
        vm.tools_mount()
        
        #vm.ping_until()
        #vm.ping_until(until='DOWN')
        vm.is_started(timeout=600)
        vm.tools_umount()
    
    def up_down(self, vm, count):
        self.logging_info('up_down')
        if not vm.is_down(timeout=2, err=False):
            vm.poweroff()
            vm.is_down(timeout=10)
        
        for x in xrange(count):    
            vm.start()
            vm.is_started(timeout=200)
            time.sleep(20)
            vm.shutdown()
            vm.is_down()
            logging.info("up_down: " + str(x))
            
    def reboot_vm(self, vm, count):
        self.logging_info('reboot_vm')
        if vm.is_down(timeout=2, err=False):
            vm.start()
            vm.is_started(timeout=200)
            
        time.sleep(15)
        for x in xrange(count):
            vm.pw_restart()
            time.sleep(20)
            vm.is_started(timeout=250)
            time.sleep(5)
            logging.info("power restart: " + str(x))

        for x in xrange(count):
            vm.restart()
            time.sleep(20)
            vm.is_started(timeout=200)
            time.sleep(5)
            logging.info("reboot_vm: " + str(x))

    def pause_vm(self, vm, count):
        self.logging_info('pause_vm')

        if vm.is_down(timeout=2, err=False):
            vm.start()
            vm.is_started()

        for x in range(count):
            logging.info('loop %s/%s' % (str(x), str(count-1)))
            vm.pause()
            vm.is_down()
            time.sleep(2)
            vm.start()
            vm.is_started()

    
    def clone_vms(self, vm, numb):
        self.logging_info('clone_vms')
        self.clones = []
        for x in range(numb):
            logging.info('cloning ' + str(x))
            clone = self.handler.clone_vm(vm, 'clone-' + str(x),
                                  'defaultlocal', level='high')
            self.clones.append(clone)
            time.sleep(1)

        for c in self.clones:
            c.start()
            print "??"
        
        for c in self.clones:
            c.is_started(timeout=400)

        for c in self.clones:
            c.poweroff()
            c.is_down(100)

    def take_snapshot(self, vm, count):
        self.logging_info('take_snapshot')
        
        if vm.is_down(timeout=2, err=False):
            vm.start()
            vm.is_started(timeout=200)
        
        for x in range(count):
            logging.info('loop %s/%s' % (str(x), str(count-1)))
            self.handler.snapshot(vm, str(x))
            time.sleep(5)

    def rec_snapshot(self, vm, count):
        self.logging_info('rec_snapshot')
        
        for x in range(count):
            logging.info('loop %s/%s' % (str(x), str(count-1)))
            snaps = vm.get_snapshots()

            if snaps:
                snap = random.choice(snaps)
                if not self.query.is_current_snapshot(snap):
                    self.handler.recover_snapshot(vm, snap)
                    vm.is_started(timeout=180)
                    time.sleep(10)

    def copy_to_template(self, vm):
        self.logging_info('copy to template')

        dest_name = 'copy2temp'
        temp = self.handler.clone_vm(vm, dest_name, 'defaultlocal',
                                     to_temp=True, level='high')

        return temp
            

    def to_template(self, vm):
        self.logging_info('to_template')

        dest_name = 'au_template'
        self.handler.conv_to_template(vm)

    
    def backup(self, vm, count):
        self.logging_info('backup')

        for x in range(count):
            logging.info('loop %s/%s' % (str(x),str(count-1)))
            back_numb = x + 1
            self.handler.backup_vm(vm, 'defaultlocal')
            time.sleep(3)
            self.handler.recover_backup('backup_recov' + str(x), vm,
                                        'defaultlocal', back_numb)

        vms = []
        for x in range(count):
            vm = self.vserver.get_exist_vm('backup_recov' + str(x))
            vms.append(vm)
            vm.start()
            vm.is_started(timeout=200)

        for x in vms:
            x.poweroff()
            x.is_down()


    def diff_clone(self, temp, count, basename):
        self.logging_info('diff clone')

        rw_diff = self.handler.diff_clone(temp, basename + 'rw',
                                          typ='rw', number=count)
        ro_diff = self.handler.diff_clone(temp, basename + 'ro',
                                          typ='ro', number=count)
        def boot_check(vm_list):
            vms = []
            for x in vm_list:
                vm = self.vserver.get_vm_by_uuid(x)
                vms.append(vm)
                print vm.name
                vm.start()

            for x in vms:
                vm.is_started(timeout=200)

            for x in vms:
                x.poweroff()
                x.is_down()
            
        boot_check(rw_diff)
        boot_check(ro_diff)


    
    def testStability(self):
        self.mount_storage()
        time.sleep(1)
        self.copy_img()
        time.sleep(1)
        vm = self.create_vm('auto-seed')
        self.tools_install(vm)
        
        self.up_down(vm, 1)
        time.sleep(20)
        self.reboot_vm(vm, 1)

        time.sleep(5)
        vm = self.vserver.get_exist_vm('auto-seed')
        self.pause_vm(vm, 3)
        self.clone_vms(vm, 3)
        vm1 = self.vserver.get_exist_vm('clone-0')
        vm2 = self.vserver.get_exist_vm('clone-1')
        vm3 = self.vserver.get_exist_vm('clone-2')
        self.take_snapshot(vm1, 6)
        time.sleep(2)
        self.rec_snapshot(vm1, 5)
        self.backup(vm2, 3)

        #temp1 = self.copy_to_template(vm3)
        #self.diff_clone(temp1, 1, 'diff_clone1')
        self.to_template(vm3)
        self.diff_clone(vm3, 5, 'diff_clone2')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
