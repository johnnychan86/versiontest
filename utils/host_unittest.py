'''
Created on Sep 3, 2012

@author: johnny
'''
import unittest
import hosts

class Test(unittest.TestCase):


    def testName(self):
        host = hosts.create_host('192.168.200.6')
        #result = host.run('cat dag.repo')
        #host.get_file('dag.repo', '')
        result = host.run('mount')
        print result.stdout.strip()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()