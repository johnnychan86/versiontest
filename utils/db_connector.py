#-*- coding:utf-8 -*-
'''
Created on Jul 26, 2012

@author: johnny
'''
import traceback
import time
import logging 

RECONNECT_FOREVER = object()

class PsqlBackend(object):
    def __init__(self):
        #import pgdb
        #self._db_module = pgdb
        #self._connection = None
        #self._cursor = None
        
        try:
            import psycopg2 as psql
        except ImportError:
            import pgdb as psql
            
        self._db_module = psql
        
        self._connection = None
        self._cursor = None
    
    def connect(self, host=None, port=None, 
                username=None, password=None, db_name=None):
        self._connection = self._db_module.connect(
                               database=db_name, host=host, 
                               user=username, password=password)
        self._cursor = self._connection.cursor()
        self._connection.autocommit = True
        
    
    def disconnect(self):
        if self._connection:
            self._connection.close()
        self._connection = None
        self._cursor = None
    
    def execute(self, operation, parameters):
        self._cursor.execute(operation, parameters)
        self.rowcount = self._cursor.rowcount
        if "INSERT" in operation:
            return None
        else:
            return self._cursor.fetchall()
        
        
class MySQLBackend(object):
    def __init__(self):
        try: 
            import MySQLdb as mysql
        except ImportError:
            print "cannot import mysqldb"
            
        self._db_module = mysql
        
        self._connection = None
        self._cursor = None
        
    def connect(self, host=None, port=None, 
                username=None, password=None, db_name=None):
        self._connection = self._db_module.connect(
                               db=db_name, host=host, 
                               user=username, passwd=password)
        self._cursor = self._connection.cursor()
        
    
    def disconnect(self):
        if self._connection:
            self._connection.close()
        self._connection = None
        self._cursor = None
    
    def execute(self, operation, parameters):
        self._cursor.execute(operation, parameters)
        self.rowcount = self._cursor.rowcount
        return self._cursor.fetchall()


class DataBaseConnection(object):
    def __init__(self):        
        self._backend = None
        self.db_type = None
        self.host = None
        self.port = None
        self.user = None
        self.passwd = None
        self.db_name = None
        
        # reconnect defaults
        self.reconnect_enabled = True
        self.reconnect_delay_sec = 20
        self.max_reconnect_attempts = 10
    
    def set_options(self, db_type=None, host=None, 
                    port=None, user=None, passwd=None, db_name=None):
        self.db_type = db_type
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.db_name = db_name
        
    
    def _is_reconnect_enabled(self, supplied_param):
        if supplied_param is not None:
            return supplied_param
        return self.reconnect_enabled
    
    def _reached_max_attempts(self, num_attempts):
        return (self.max_reconnect_attempts is not RECONNECT_FOREVER and
                num_attempts > self.max_reconnect_attempts)
    
    #def _connect_backend(self):
    
    def get_backend(self, db_type):
        '''Need to expand for more backends'''
        if db_type == "psql":
            self._backend = PsqlBackend()
        elif db_type == 'mysql':
            self._backend = MySQLBackend()
    
    def _connect(self, try_reconnecting=None):
        num_attempts = 0
        while True:
            try:
                self._backend.connect(host=self.host, port=self.port,
                                      username=self.user,
                                      password=self.passwd,
                                      db_name=self.db_name)
                return
            except Exception:
                num_attempts += 1
                if not self._is_reconnect_enabled(try_reconnecting):
                    raise
                if self._reached_max_attempts(num_attempts):
                    raise
                traceback.print_exc()
                print ("Can't connect to database; reconnecting in %s sec" %
                       self.reconnect_delay_sec)
                time.sleep(self.reconnect_delay_sec)
                self.disconnect()
    
    def connect(self, db_type=None, host=None, port=None, 
                user=None, passwd=None, db_name=None):
        self.get_backend(db_type)
        self.disconnect()
        
        self.set_options(db_type, host, port, user, passwd, db_name)
        self._connect()
            
    
    def disconnect(self):
        if self._backend:
            self._backend.disconnect()
        
    def execute(self, operation, parameters=None, try_reconnecing=None):
        try:
            result = self._backend.execute(operation, parameters)
        except Exception:
            if not self._is_reconnect_enabled(try_reconnecing):
                raise
            traceback.print_exc()
            print ("Connection died; reconnecting")
            self.disconnect()
            self._connect(try_reconnecing)
            result = self._backend.execute(operation, parameters)
            
        return result
    
    