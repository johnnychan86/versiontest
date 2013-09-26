'''
Created on 2012-8-6

@author: johnny
'''
import unittest
import zmq_client


class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testName(self):
        zmq_client.test()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()