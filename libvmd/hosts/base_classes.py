# Copyright 2009 Google Inc. Released under the GPL v2

"""
This module defines the base classes for the Host hierarchy.

Implementation details:
You should import the "hosts" package instead of importing each type of host.

        Host: a machine on which you can run programs
"""

import cPickle, cStringIO, logging, os, re
import utils.base_utils as utils
import error 

'''
Base host has:
is_available: ping host, figure out if it is started up
reboot: command way, I mean need send reboot message by zmq
wait_for_up: wait for host up
listener: maybe can run a listener on the host
get_file: useful
send_file: great
run: important! run command on host!!!
'''


class Host(object):
    """
    This class represents a machine on which you can run programs.

    It may be a local machine, the one autoserv is running on, a remote
    machine or a virtual machine.

    Implementation details:
    This is an abstract class, leaf subclasses must implement the methods
    listed here. You must not instantiate this class but should
    instantiate one of those leaf subclasses.

    When overriding methods that raise NotImplementedError, the leaf class
    is fully responsible for the implementation and should not chain calls
    to super. When overriding methods that are a NOP in Host, the subclass
    should chain calls to super().
    """

    DEFAULT_REBOOT_TIMEOUT = 1800
    WAIT_DOWN_REBOOT_TIMEOUT = 840
    WAIT_DOWN_REBOOT_WARNING = 540
    HOURS_TO_WAIT_FOR_RECOVERY = 2.5
    # the number of hardware repair requests that need to happen before we
    # actually send machines to hardware repair
    HARDWARE_REPAIR_REQUEST_THRESHOLD = 4


    def __init__(self, *args, **dargs):
        self._initialize(*args, **dargs)


    def _initialize(self, *args, **dargs):
        self._already_repaired = []
        self._removed_files = False
        self.env = {}


    def close(self):
        pass


    def setup(self):
        pass


    def run(self, command, timeout=3600, ignore_status=False,
            stdin=None, args=()):
        """
        Run a command on this host.

        @param command: the command line string
        @param timeout: time limit in seconds before attempting to
                kill the running process. The run() function
                will take a few seconds longer than 'timeout'
                to complete if it has to kill the process.
        @param ignore_status: do not raise an exception, no matter
                what the exit code of the command is.
        @param stdin: stdin to pass (a string) to the executed command
        @param args: sequence of strings to pass as arguments to command by
                quoting them in " and escaping their contents if necessary

        @return a utils.CmdResult object

        @raises AutotestHostRunError: the exit code of the command execution
                was not 0 and ignore_status was not enabled
        """
        raise NotImplementedError('Run not implemented!')


    def run_output(self, command, *args, **dargs):
        return self.run(command, *args, **dargs).stdout.rstrip()


    def reboot(self):
        raise NotImplementedError('Reboot not implemented!')

    def get_file(self, source, dest, delete_dest=False):
        raise NotImplementedError('Get file not implemented!')


    def send_file(self, source, dest, delete_dest=False):
        raise NotImplementedError('Send file not implemented!')

#    def is_up(self):
#        raise NotImplementedError('Is up not implemented!')


    def is_shutting_down(self):
        """ Indicates is a machine is currently shutting down. """
        # runlevel() may not be available, so wrap it in try block.
        try:
            runlevel = int(self.run("runlevel").stdout.strip().split()[1])
            return runlevel in (0, 6)
        except Exception:
            return False


    def get_boot_id(self, timeout=60):
        """ Get a unique ID associated with the current boot.

        Should return a string with the semantics such that two separate
        calls to Host.get_boot_id() return the same string if the host did
        not reboot between the two calls, and two different strings if it
        has rebooted at least once between the two calls.

        @param timeout The number of seconds to wait before timing out.

        @return A string unique to this boot or None if not available."""
        BOOT_ID_FILE = '/proc/sys/kernel/random/boot_id'
        NO_ID_MSG = 'no boot_id available'
        cmd = 'if [ -f %r ]; then cat %r; else echo %r; fi' % (
                BOOT_ID_FILE, BOOT_ID_FILE, NO_ID_MSG)
        boot_id = self.run(cmd, timeout=timeout).stdout.strip()
        if boot_id == NO_ID_MSG:
            return None
        return boot_id


#    def wait_up(self, timeout=None):
#        raise NotImplementedError('Wait up not implemented!')


#    def wait_down(self, timeout=None, warning_timer=None, old_boot_id=None):
#        raise NotImplementedError('Wait down not implemented!')
#
#
#    def wait_for_restart(self, timeout=DEFAULT_REBOOT_TIMEOUT,
#                         down_timeout=WAIT_DOWN_REBOOT_TIMEOUT,
#                         down_warning=WAIT_DOWN_REBOOT_WARNING,
#                         log_failure=True, old_boot_id=None, **dargs):
#        """ Wait for the host to come back from a reboot. This is a generic
#        implementation based entirely on wait_up and wait_down. """
#        if not self.wait_down(timeout=down_timeout,
#                              warning_timer=down_warning,
#                              old_boot_id=old_boot_id):
#            if log_failure:
#                self.record("ABORT", None, "reboot.verify", "shut down failed")
#            raise error.HostShutdownError("Host did not shut down")
#
#        if self.wait_up(timeout):
#            self.record("GOOD", None, "reboot.verify")
#            self.reboot_followup(**dargs)
#        else:
#            self.record("ABORT", None, "reboot.verify",
#                        "Host did not return from reboot")
#            raise error.AutoservRebootError("Host did not return from reboot")


    def check_diskspace(self, path, gb):
        """Raises an error if path does not have at least gb GB free.

        @param path The path to check for free disk space.
        @param gb A floating point number to compare with a granularity
            of 1 MB.

        1000 based SI units are used.

        @raises AutoservDiskFullHostError if path has less than gb GB free.
        """
        one_mb = 10 ** 6  # Bytes (SI unit).
        mb_per_gb = 1000.0
        logging.info('Checking for >= %s GB of space under %s on machine %s',
                     gb, path, self.hostname)
        df = self.run('df -PB %d %s | tail -1' % (one_mb, path)).stdout.split()
        free_space_gb = int(df[3]) / mb_per_gb
        if free_space_gb < gb:
            pass
            #raise error.AutoservDiskFullHostError(path, gb, free_space_gb)
        else:
            logging.info('Found %s GB >= %s GB of space under %s on machine %s',
                free_space_gb, gb, path, self.hostname)


    def get_open_func(self, use_cache=True):
        """
        Defines and returns a function that may be used instead of built-in
        open() to open and read files. The returned function is implemented
        by using self.run('cat <file>') and may cache the results for the same
        filename.

        @param use_cache Cache results of self.run('cat <filename>') for the
            same filename

        @return a function that can be used instead of built-in open()
        """
        cached_files = {}

        def open_func(filename):
            if not use_cache or filename not in cached_files:
                output = self.run('cat \'%s\'' % filename,
                                  stdout_tee=open('/dev/null', 'w')).stdout
                fd = cStringIO.StringIO(output)

                if not use_cache:
                    return fd

                cached_files[filename] = fd
            else:
                cached_files[filename].seek(0)

            return cached_files[filename]

        return open_func


    def _get_mountpoint(self, path):
        """Given a "path" get the mount point of the filesystem containing
        that path."""
        code = ('import os\n'
                # sanitize the path and resolve symlinks
                'path = os.path.realpath(%r)\n'
                "while path != '/' and not os.path.ismount(path):\n"
                '    path, _ = os.path.split(path)\n'
                'print path\n') % path
        return self.run('python -c "%s"' % code,
                        stdout_tee=open(os.devnull, 'w')).stdout.rstrip()


    def erase_dir_contents(self, path, ignore_status=True, timeout=3600):
        """Empty a given directory path contents."""
        rm_cmd = 'find "%s" -mindepth 1 -maxdepth 1 -print0 | xargs -0 rm -rf'
        self.run(rm_cmd % path, ignore_status=ignore_status, timeout=timeout)
        self._removed_files = True


    def disable_ipfilters(self):
        """Allow all network packets in and out of the host."""
        self.run('iptables-save > /tmp/iptable-rules')
        self.run('iptables -P INPUT ACCEPT')
        self.run('iptables -P FORWARD ACCEPT')
        self.run('iptables -P OUTPUT ACCEPT')


    def enable_ipfilters(self):
        """Re-enable the IP filters disabled from disable_ipfilters()"""
        if self.path_exists('/tmp/iptable-rules'):
            self.run('iptables-restore < /tmp/iptable-rules')


    def cleanup(self):
        pass


    def start_loggers(self):
        """ Called to start continuous host logging. """
        pass


    def stop_loggers(self):
        """ Called to stop continuous host logging. """
        pass


    # some extra methods simplify the retrieval of information about the
    # Host machine, with generic implementations based on run(). subclasses
    # should feel free to override these if they can provide better
    # implementations for their specific Host types

    def get_num_cpu(self):
        """ Get the number of CPUs in the host according to /proc/cpuinfo. """
        proc_cpuinfo = self.run('cat /proc/cpuinfo',
                                stdout_tee=open(os.devnull, 'w')).stdout
        cpus = 0
        for line in proc_cpuinfo.splitlines():
            if line.startswith('processor'):
                cpus += 1
        return cpus


    def get_arch(self):
        """ Get the hardware architecture of the remote machine. """
        arch = self.run('/bin/uname -m').stdout.rstrip()
        if re.match(r'i\d86$', arch):
            arch = 'i386'
        return arch


    def get_kernel_ver(self):
        """ Get the kernel version of the remote machine. """
        return self.run('/bin/uname -r').stdout.rstrip()


    def get_cmdline(self):
        """ Get the kernel command line of the remote machine. """
        return self.run('cat /proc/cmdline').stdout.rstrip()


    def get_meminfo(self):
        """ Get the kernel memory info (/proc/meminfo) of the remote machine
        and return a dictionary mapping the various statistics. """
        meminfo_dict = {}
        meminfo = self.run('cat /proc/meminfo').stdout.splitlines()
        for key, val in (line.split(':', 1) for line in meminfo):
            meminfo_dict[key.strip()] = val.strip()
        return meminfo_dict


    def path_exists(self, path):
        """ Determine if path exists on the remote machine. """
        result = self.run('ls "%s" > /dev/null' % utils.sh_escape(path),
                          ignore_status=True)
        return result.exit_status == 0


    # some extra helpers for doing job-related operations

#    def record(self, *args, **dargs):
#        """ Helper method for recording status logs against Host.job that
#        silently becomes a NOP if Host.job is not available. The args and
#        dargs are passed on to Host.job.record unchanged. """
#        if self.job:
#            self.job.record(*args, **dargs)


    def log_kernel(self):
        """ Helper method for logging kernel information into the status logs.
        Intended for cases where the "current" kernel is not really defined
        and we want to explicitly log it. Does nothing if this host isn't
        actually associated with a job. """
        if self.job:
            kernel = self.get_kernel_ver()
            self.job.record("INFO", None, None,
                            optional_fields={"kernel": kernel})


    def log_reboot(self, reboot_func):
        """ Decorator for wrapping a reboot in a group for status
        logging purposes. The reboot_func parameter should be an actual
        function that carries out the reboot.
        """
        if self.job and not hasattr(self, "RUNNING_LOG_REBOOT"):
            self.RUNNING_LOG_REBOOT = True
            try:
                self.job.run_reboot(reboot_func, self.get_kernel_ver)
            finally:
                del self.RUNNING_LOG_REBOOT
        else:
            reboot_func()


    def list_files_glob(self, glob):
        """
        Get a list of files on a remote host given a glob pattern path.
        """
        SCRIPT = ("python -c 'import cPickle, glob, sys;"
                  "cPickle.dump(glob.glob(sys.argv[1]), sys.stdout, 0)'")
        output = self.run(SCRIPT, args=(glob,), stdout_tee=None,
                          timeout=60).stdout
        return cPickle.loads(output)

