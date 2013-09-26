#-*- coding:utf-8 -*-
'''
Created on 2012-8-16

@author: johnny
'''
import platform
import os
import subprocess
import time

def ping(ip):
    if not ip:
        return False
    
    if platform.system() == 'Linux':
        cmd = "ping -W 2 -c 1 %s" % ip
        print "ping: pinging %s ......" % ip
        pp = subprocess.Popen(['ping', '-c1', '-W2', ip])
        count = 0
        while count < 3:
            rc = pp.poll()
            if pp.returncode is not None:
                break
            count = count + 1
            time.sleep(2)
        else:
            pp.kill()
            pp.wait()
            rc = 1
            
        if rc:
            return False

    return True

#Just one shot
#def ping(ip, timeout=10):
#    if not ip:
#        return
#    
#    if platform.system() == 'Linux':
#        cmd = "ping -c 1 %s -w %s" % (ip, timeout)
#        print "ping: pinging %s ......" % ip
#        if os.system(cmd):
#            return False        
#    elif platform.system() == 'Windows':
#        cmd = 'ping -n 1 %s' % ip
#        print "pinging %s ......" % ip
#        reply = os.popen(cmd).readlines()
#        for s in reply:
#            s = s.decode('gbk')
#            if s.find("无法访问") >= 0 or s.find("Ureachable") >= 0:
#                return False
#    return True


if __name__ == "__main__":
    print ping("192.168.200.10")
