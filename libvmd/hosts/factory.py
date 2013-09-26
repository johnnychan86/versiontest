'''
Created on Sep 3, 2012

@author: johnny
'''
from utils import base_utils as utils
import ssh_host

def create_host(hostname, **args):
    # parse out the profile up-front, if it's there, or else console monitoring
    # will not work
    
    classes = [ssh_host.SSHHost]

    # create a custom host class for this machine and return an instance of it
    host_class = type("%s_host" % hostname, tuple(classes), {})
    host_instance = host_class(hostname, **args)

    return host_instance
