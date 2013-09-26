'''
Created on Jul 26, 2012

@author: johnny
'''
import unittest
import db_connector

class Test(unittest.TestCase):


    def setUp(self):
        self.db = db_connector.DataBaseConnection()


    def tearDown(self):
        print "OK!"


    def testName(self):
        self.db.connect('psql', "192.168.3.100", 5432, 'postgres', '', 'fronware')
        result = self.db.execute("SELECT * from storage where id=6")
        print result
        self.db.disconnect()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()