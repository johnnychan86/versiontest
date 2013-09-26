'''
Created on Sep 28, 2012

@author: johnny
'''
import unittest, re, os, sys

import error
import cases
import const

class Test(object):
    def __init__(self):
        self.suite = unittest.TestSuite()
        self.result = unittest.TestResult()
    
    def add_test_by_name(self, name):
        self.test_name = name
        loader = unittest.TestLoader()
        print "Loadding...", 'case.' + name
        
        try:
            try:
                self.suite = loader.loadTestsFromName('cases.' + name)
            except ImportError:
                raise error.CommonError("Load test case failed: %s" % name)
            print "Done."
        except AttributeError:
            msg = "The test case %s cannot be load!" % name
            raise error.CommonError(msg)
    
    def get_results(self):
        return self.result
    
    def get_test_name(self):
        return self.test_name
    
    def run_test(self):
        self.get_test_name()
        if not self.suite.countTestCases():
            raise error.CommonError("No tests to run, load the test!")
        self.result =  \
        unittest.TextTestRunner(stream = sys.stdout).run(self.suite)
        
