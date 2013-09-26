#! /usr/bin/env python

import pexpect, pxssh
import time

def touch(host):
    cmd = 'touch web_ip'
    cmd2 = 'echo "10.10.48.22" >> web_ip'
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


if __name__ == "__main__":
    touch('10.10.200.6')
