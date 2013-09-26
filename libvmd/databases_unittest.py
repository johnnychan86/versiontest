'''
Created on 2012-8-1

@author: johnny
'''
import unittest
import databases

class Test(unittest.TestCase):


    def setUp(self):
        self.query = databases.DBQuery('10.10.51.220', 'postgres')


    def tearDown(self):
        pass
    
    def testVMimg(self):
        print self.query.get_snapshots('clone-0')
        print self.query.get_vm_ip('aaa')
        print self.query.get_vm_name('tDcgWxfK-nmp6cR-dYMt')
#        print self.query.get_vm_baseimg('xp-4')
#        print self.query.get_snapshots('xp-4')
#        print self.query.is_current_snapshot("1358477266_babe5f76-CgpbJG-a833")
        #print self.qurey.get_vm_img('xp-a')

#    def testHostUuid(self):
#        result = self.qurey.get_hostUuid()
#        print 'testHostUuid: ' + result
#    
#    def testStorageUuid(self):
#        result = self.qurey.get_storageUuid("description=\'defaultlocal\'")
#        print result
#        
#    def testStoragePath(self):
#        print self.qurey.get_storagepath()
#        
#    def testVmuuid(self):
#        print self.qurey.get_vmUuid()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()