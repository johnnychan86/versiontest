#!/usr/bin/env python
#-*- coding:utf-8 -*-
import os
import logging 
import time
import datetime

import const
from utils import logging_config
from utils import logging_manager


HOME_PATH = const.HOME_PATH

class CommonLoggingConfig(logging_config.LoggingConfig):
    pass


class TestEngine(object):

    def __init__(self):
        self.states = {}
        self.current = None
        self.prev = None
        self.s_stack = []
        self.skip_list = []
        logging_manager.configure_logging(CommonLoggingConfig(), 
                use_console=True, verbose=False)
        self.logging = logging_manager.get_logging_manager(
                manage_stdout_and_stderr=True, redirect_fds=True)

        if not os.path.exists(HOME_PATH):
            os.makedirs(HOME_PATH)

    def add_state(self, state):
        self.states[str(state)] = state

    def set_start(self):
        self.current = "START"

    def set_state(self, state):
        self.current = state

    def start_logging(self):
        self.logging.start_logging()
        
    def run(self, args):
        self.start_time = \
            datetime.datetime.now().strftime("%Y%m%d_%H%M%S.%f")
        log_dir = os.path.join(HOME_PATH, 'log')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_file = os.path.join(log_dir, self.start_time)
        log_file = os.path.abspath(log_file)
        self.start_logging()
        self.logging.tee_redirect(log_file)

        current = self.states[self.current]
        while 1:
            prev = self.current
            self.set_state(current.next())
            if self.current == "FINAL":
                break
            current = self.states[self.current]
            current.run(prev, **args)
    
    
        

