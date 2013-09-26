#-*- coding:utf-8 -*-
import json, logging
import zmq
   
def zmq_sender(msg, host, port):
    context = zmq.Context()
    #Only byte string is acceptable or will receive TypeError
    message = str(msg)
    # Socket to talk to server
    socket = context.socket(zmq.REQ)
    dest = "tcp://" + host + ":" + str(port)
    socket.connect(dest)
    socket.send(message)
    recv_msg = socket.recv()
    logging.debug(recv_msg)
    socket.close()
    logging.debug("socket close")

    
    
    