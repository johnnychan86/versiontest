#-*- coding:utf-8 -*-
'''
Created on 2012-8-14

@author: johnny
'''
import threading
import time
import json
import zmq

black_list = ['monit', 'log']

class Listener(threading.Thread):
    def __init__(self, result, port=9081):
        threading.Thread.__init__(self, name="listener")
        self.result = result
        self.port = port
        self.setDaemon(True)
        self.start()
        
    def run(self):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        dest = "tcp://*:" + str(self.port)
        """
        Only one instance can bind to port, 
        if there is another thread working,
        this thread do nothing and exit.
        """
        try:
            socket.bind(dest)
        except Exception:
            return
        
        while True:
            recv_msg = socket.recv()
            socket.send("Auto response")
            msg = self.decode_msg(recv_msg)
            #print "Listener: msg", msg
            if msg['message'] and msg['message'] not in black_list:
                self.result.put(msg)
            
            time.sleep(0.2)
    
    def decode_msg(self, msg):
        return json.loads(msg)
    
    
    
    