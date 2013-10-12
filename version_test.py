#! /usr/bin/env python
#-*- coding:utf-8 -*-

import sys
from optparse import OptionParser

from engine import TestEngine
import state

def main():
    usage = "usage: version_test.py -s|--system -p|--path"
    parser = OptionParser(usage=usage)
    parser.add_option('-p', '--path', action='store', dest='path',
            help="Version path")
    parser.add_option('-s', '--system', action='store', dest='system',
            help="The name of system registered in cobbler")
    parser.add_option('-n', '--not-reimport', action='store_true', 
            dest='reimport', help="Do not re-import the distro")
    parser.add_option('-d', '--direct-test', action='store_true', 
            dest='direct', help="Set direct test")
    parser.add_option('-o', '--skip-install', action='store_true',
            dest='skip_install', help="Skip the server insallation")

    (options, args) = parser.parse_args()
    path = ''
    system = ''
    reimport = True
    direct = False
    skip_install = False

    if options.path:
        path = options.path
    if options.system:
        system = options.system
    if options.reimport:
        reimport = False
    if options.direct:
        direct = True
    if options.skip_install:
        skip_install = True

    if not path or not system:
        parser.print_help()
        sys.exit(1)

    test_engine = TestEngine()
    test_engine.add_state(state.Start())
    test_engine.add_state(state.Error())
    test_engine.add_state(state.Initialize())
    test_engine.add_state(state.CobblerInit())
    test_engine.add_state(state.StartInstall())
    test_engine.add_state(state.CheckInstallState())
    test_engine.add_state(state.ServerInit())
    test_engine.add_state(state.RunTest())

    data = {
            'sys': system,
            'path': path,
            'reimport': reimport,
            'direct': direct
            }

    test_engine.set_start()
    test_engine.run(data)


if __name__ ==  "__main__":
    main()
