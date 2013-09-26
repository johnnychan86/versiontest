#-*- coding:utf-8 -*-
'''
Created on Aug 29, 2012

@author: johnny
'''

class CommonError(Exception):
    def __init__(self, msg):
        self.msg = msg
        
    def __str__(self):
        return Exception.__str__(self) + self.msg


def exception_context(e):
    """Return the context of a given exception (or None if none is defined)."""
    if hasattr(e, "_context"):
        return e._context
    
    
def _context_message(e):
    s = exception_context(e)
    if s:
        return "    [context: %s]" % s
    else:
        return ""


class MBaseException(Exception):
    def __str__(self):
        return Exception.__str__(self) + _context_message(self)

    
class TestBaseException(MBaseException):
    """The parent of all test exceptions."""
    # Children are required to override this.  Never instantiate directly.
    exit_status="NEVER_RAISE_THIS"


class TestError(TestBaseException):
    """Indicates that something went wrong with the test harness itself."""
    exit_status="ERROR"


class VMStartUpTimeoutError(TestError):
    def __str__(self):
        return Exception.__str__(self) + "Vm start failed or cannot connect"

class VMShutdownTimeoutError(TestError):
    def __str__(self):
        return Exception.__str__(self) + "VM shutdown timed out"
    
class OperationTimeoutException(Exception):
    def __init__(self, timeout):
        self.timeout = timeout
        
    def __str__(self):
        return Exception.__str__(self) + "Operation Timeout %s" % self.timeout

class OperationFailedError(TestError):
    def __init__(self, msg):
        self.msg = msg
        
    def __str__(self):
        return Exception.__str__(self) + "Operation Failed %s" % self.msg


class HostError(Exception):
    pass


class HostShutdownError(HostError):
    def __init__(self, msg):
        self.msg = msg
        
    def __str__(self):
        return Exception.__str__(self) + self.msg


class HostSSHTimeout(HostError):
    pass


class HostSshPermissionDeniedError(HostError):
    pass


class HostRunError(HostError):
    pass


class HostSshPingError(HostError):
    pass


class HostIsShuttingDownError(HostError):
    pass

    
class CmdError(TestError):
    """\
    Indicates that a command failed, is fatal to the test unless caught.
    """
    def __init__(self, command, result_obj, additional_text=None):
        TestError.__init__(self, command, result_obj, additional_text)
        self.command = command
        self.result_obj = result_obj
        self.additional_text = additional_text

    def __str__(self):
        if self.result_obj.exit_status is None:
            msg = "Command <%s> failed and is not responding to signals"
            msg %= self.command
        else:
            msg = "Command <%s> failed, rc=%d"
            msg %= (self.command, self.result_obj.exit_status)

        if self.additional_text:
            msg += ", " + self.additional_text
        msg += _context_message(self)
        msg += '\n' + repr(self.result_obj)
        return msg