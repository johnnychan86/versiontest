import unittest

class TestC(unittest.TestCase):

    def setUp(self):
        print "yes, setup"

    def tearDown(self):
        print "yes, teardown"

    def testa(self):
        print "this is main body"


