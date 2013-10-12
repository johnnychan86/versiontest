#!/usr/bin/env python
#-*- coding:utf-8 -*-
import os
import logging 
import time
import pexpect, pxssh
from subprocess import Popen
from subprocess import PIPE

from utils import ping
import test
import const


class State(object):
    def __init__(self, name): self.name = name
    
    def __str__(self): return self.name
    
    def run(self):
        assert 0, "Not implemented"

    def next(self):
        assert 0, "Not implemented"


class Start(State):
    def __init__(self):
        State.__init__(self, "START")

    def run(self, prev, **args):
        logging.info("*** Start...")
        return

    def next(self):
        return "Initialize"


class Error(State):
    def __init__(self):
        State.__init__(self, 'error')
        self.prev = None
        self.path = None
        self.system = None

    def run(self, prev, **args):
        logging.info("*** %s ***" % self.name)
        self.prev = prev

    def next(self):
        logging.error("Failed on step %s" % str(self.prev))
        return "FINAL"

def get_version(path):
    version = os.path.basename(path).split('_')[1]
    t = version.split('.')
    if t[-1] == 'iso':
        version = ''.join(t[:-1])
    else:
        version = ''.join(t)
    return version

def get_distros():
    cmd = "cobbler distro list"
    stdout = Popen(cmd, shell=True, stdout=PIPE).stdout
    return [x.strip() for x in stdout]


class Initialize(State):
    def __init__(self):
        State.__init__(self, "Initialize")

    def run(self, prev, **args):
        logging.info("*** %s ***" % self.name)
        self.prev = prev
        self.path = args['path']
        self.system = args['sys']
        self.re_import = args['reimport']
        self.direct_flag = args['direct']
        self.skip_install = args['skip_install']

    def next(self):
        curr_profile = get_state(self.system, 'Profile')
        profile = "%s-x86_64" % get_version(self.path)

        if self.direct_flag:
            return "RunTest"
        if self.skip_install:
            return "ServerInit"
        if not curr_profile:
            self.create_system()
        if not profile in get_distros():
            return "CobblerInit"
        if not self.re_import:
            return "StartInstall"

        if curr_profile == profile:
            rc = self.remove_all(profile)
            if rc:
                return 'error'
        else:
            rc = self.remove_distro(profile)
            if rc:
                return 'error'
           
        return "CobblerInit"

    def remove_all(self, profile):
        print "Remove all !!!!!!!"
        cmd = "cobbler system remove --name=%s" % self.system
        rc = os.system(cmd)
        if rc:
            return rc
        self.remove_distro(profile)

        rc = self.create_system()
        if rc:
            return rc
        cmd = "cobbler sync"
        rc = os.system(cmd)
        if rc:
            return rc
        return 0

    def remove_distro(self, profile):
        print "remove_distro"
        cmd = "cobbler profile remove --name=%s" % profile
        rc = os.system(cmd)
        if rc:
            return rc

        time.sleep(1)

        cmd = "cobbler distro remove --name=%s" % profile
        rc = os.system(cmd)
        if rc:
            return rc

        cmd = "cobbler sync"
        rc = os.system(cmd)
        if rc:
            return rc
        return 0

    def create_system(self):
        logging.info("-*-* Create new system")
        node_info = {}
        node_info.update(const.NODE1)
        node_info['name'] = self.system
        cmd = "cobbler system add --name=%(name)s \
               --hostname=%(host-name)s \
               --profile=%(profile)s  \
               --interface=%(interface)s \
               --mac=%(mac)s \
               --ip-address=%(ip)s \
               --subnet=%(subnet)s \
               --gateway=%(gateway)s \
               --name-servers=%(name-servers)s \
               --static=%(static)s \
               --power-type=%(power-type)s \
               --power-user=%(power-user)s \
               --power-pass=%(power-passwd)s \
               --power-address=%(power-address)s" % node_info
        rc = os.system(cmd)
        if rc:
            return rc
        return 0



class CobblerInit(State):
    def __init__(self):
        State.__init__(self, "CobblerInit")
        self.prev = None
        self.path = None
        self.version = None
        self.system = None

    def run(self, prev, **args):
        logging.info("*** %s ***" % self.name)
        self.prev = prev
        self.path = args['path']
        self.system = args['sys']

    def next(self):
        if not self.path:
            #logging
            return "error"

        #e.g. self.path = "FVI/v2.9.2/Build0072/vServer_v2.9.2Build0072_FW.iso"
        self.version = os.path.basename(self.path).split('_')[1]
        t = self.version.split('.')
        if t[-1] == 'iso':
            self.version = ''.join(t[:-1])
        else:
            self.version = ''.join(t)
        rc = self.do_cobbler_import()
        if rc:
            return 'error'
        return 'StartInstall'

    def do_cobbler_import(self):
        cmd = "./ver_import.sh --pth %s --ver %s --sys %s" % \
              (self.path, self.version, self.system) 
        rc = os.system(cmd)
        
        if rc:
            return rc
        profile = get_state(self.system, 'Profile')
        cmd = "./make-installimg.sh --distro %s" % profile
        rc = os.system(cmd)
        return rc


class StartInstall(State):
    def __init__(self):
        self.prev = None
        State.__init__(self, 'StartInstall')
        self.system = None

    def run(self, prev, **args):
        logging.info("*** %s ***" % self.name)
        self.prev = prev
        self.system = args['sys']

    def next(self):
        if get_state(self.system, 'Netboot Enabled') == 'False':
            cmd = "cobbler system edit --name=%s --netboot-enabled=True" \
                    % self.system
            rc = os.system(cmd)
            if rc:
                return 'error'

        #set pxe boot for next time
        cmd = "ipmitool -I lan -H %(power-address)s \
                -U %(power-user)s \
                -P %(power-passwd)s \
                chassis bootdev pxe" % const.NODE1
        rc = os.system(cmd)
        if rc:
            return 'error'

        cmd = "cobbler system reboot --name=%s" % self.system
        rc = os.system(cmd)
        if rc:
            return 'error'
        return "CheckInstallState"


class CheckInstallState(State):
    def __init__(self):
        State.__init__(self, 'CheckInstallState')
        self.prev = None
        self.timeout = 1200 #total timeout
        self.system = None

    def run(self, prev, **args):
        logging.info("*** %s ***" % self.name)
        self.prev = prev
        self.system = args['sys']

    def next(self):
        if not self.check_install_state(self.timeout):
            return 'error'
        if not self.check_boot(600):
            return 'error'
        return "ServerInit"

    def check_install_state(self, timeout):
        current = time.time()
        endtime = current + timeout
        interval = [480, 60, 15, 5, 2]
        count = 0
        while current < endtime:
            if count >= len(interval):
                count = len(interval) - 1
            time.sleep(interval[count])
            count = count + 1
            logging.info("Checking install state...")
            if get_state(self.system, 'Netboot Enabled') == 'False':
                return True

            current = time.time()

        return False

    def check_boot(self, timeout):
        time.sleep(120)
        current = time.time()
        endtime = current + timeout
        interval = [120, 60, 30, 15, 2]
        count = 0
        while current < endtime:
            if count >= len(interval):
                count = len(interval) - 1
            time.sleep(interval[count]) 
            count = count + 1
            if ping.ping(get_state(self.system, 'IP Address')): 
                return True
            
            current = time.time() 
           
        return False
        

class ServerInit(State):
    def __init__(self):
        State.__init__(self, 'ServerInit')
        self.prev = None
        self.root_passwd = None
        
    def run(self, prev, **args):
        logging.info("*** %s ***" % self.name)
        self.prev = prev
        self.root_passwd = const.ORG_PASSWD
        self.system = args['sys']
        self.server_ip = get_state(self.system, "IP Address")

    def next(self):
        time.sleep(120)
        if not self.change_passwd(self.server_ip, oldpwd=self.root_passwd):
            return 'error'
        if not self.prepare(self.server_ip):
            return 'error'
        if not self.ssh_keygen(self.server_ip):
            return 'error'

        return 'RunTest'

    def prepare(self, host, passwd='111111'):
        
        cmd = 'touch web_ip'
        cmd2 = 'echo "%s" >> web_ip' % const.LOCAL_IP
        cmd3 = 'mv /etc/clear_vmd.py /root/'
        cmd4 = '/etc/init.d/vmd restart'

        count = 0
        while count < 3:
            try:
                s = pxssh.pxssh()
                s.login(host, 'root', '111111', login_timeout=180)
                s.sendline(cmd)
                s.sendline(cmd2)
                s.sendline(cmd3)
                s.sendline(cmd4)
                s.prompt()
                print s.before
                s.logout()
                print s.before
            except pxssh.ExceptionPxssh, e:
                print "Failed"
                print str(e)
                error_str = str(e)
                count += 1
                time.sleep(1)
            else:
                return True

        return False

    def change_passwd(self, host, oldpwd="111111", newpwd="111111", retry=5):
        home_path = "~/.ssh"
        command = "rm %s/* -rf" % home_path
        print command
        os.popen(command)

        cmd1 = 'echo -e \"%s\n%s\" | passwd root' % (newpwd, newpwd)
        count = 0
        error_str = ''
        while count < retry:
            try:
                s = pxssh.pxssh()
                s.login(host, 'root', oldpwd, login_timeout=180)
                s.sendline(cmd1)
                s.prompt()
                print s.before
                s.logout()
                print s.before
            except pxssh.ExceptionPxssh, e:
                print "pxssh failed on login."
                print str(e)
                error_str = str(e)
                count += 1
                time.sleep(1)
            except Exception:
                return False
            else:
                return True
        
        return False

    def ssh_keygen(self, host, passwd='111111'):
        #clear old keys
        home_path = "~/.ssh"
        if not os.path.exists("%s/.ssh/id_rsa.pub" % os.getenv("HOME")):
            command = "rm %s/* -rf" % home_path
            print "Clearing old keys..."
            os.popen(command)
            print "Generating rsa keys..."
            command = "ssh-keygen -f %s/id_rsa -t rsa -N ''" % home_path
            os.popen(command)
            print "Add private key..."
            command = "ssh-add"
            os.popen(command)
        
        print "Copying public key..."
        command = "/usr/bin/ssh-copy-id"
        params = ['-i', '%s/.ssh/id_rsa.pub' % os.getenv("HOME"),
                'root@%s' % host]
        print command
        child = pexpect.spawn(command, params)
        
        try:
            index = child.expect(['continue connecting \(yes/no\)',
                   '\'s password:', pexpect.EOF], timeout=8)
            print index
            if index == 0:
                child.sendline('yes')
                print child.after,child.before
                child.expect(['\'s password:', pexpect.EOF], timeout=120)
                child.sendline(passwd)
                child.sendline('\n')
                print child.after,child.before
            if index == 1:
                child.sendline(passwd)
                child.expect('password:')
                child.sendline(passwd)
                print child.after,child.before
            if index == 2:
                print child.after,child.before
                child.close()
        except pexpect.TIMEOUT:
            print child.after,child.before
            child.close()
            return False
        else:
            return True


class RunTest(State):
    def __init__(self):
        State.__init__(self, 'RunTest')
        self.prev = None
        self.test = None

    def run(self, prev, **args):
        logging.info("*** %s ***" % self.name)
        self.prev = prev
        self.test = test.Test()

    def next(self):
        self.test.add_test_by_name(const.TEST_CASES)

        try:
            self.test.run_test()
        except Exception, e:
            print str(e)
            return 'error'
        return 'FINAL'


def get_state(system_name, key):
    cmd = "cobbler system report --name=%s" % system_name
    stdout = Popen(cmd, shell=True, stdout=PIPE).stdout
    for line in stdout:
        l = line.split(':')
        k, v = l[0].strip(), l[1].strip()
        if k == key:
            return v

    return None

