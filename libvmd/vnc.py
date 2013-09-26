#-*- coding:utf-8 -*-
'''
Created on Sep 12, 2012

@author: johnny
'''
import subprocess, signal, os

def start_vnc(host, port):
    cmd = "vncviewer %s:%s" % (host, port)
    vnc_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                shell=True, preexec_fn=os.setpgrp)
    return vnc_proc

def stop_vnc(vnc_proc):
    if isinstance(vnc_proc, subprocess.Popen):
        os.killpg(vnc_proc.pid, signal.SIGTERM)