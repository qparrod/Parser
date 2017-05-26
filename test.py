#!/usr/bin/python2.7

import re

class Parser:
    def __init__(self):
        global files
        self.regex=''
        self.type=""
        self.files = files
        self.regex = None
        self.map = {}
       
    def search(self, _string):
        m = self.regex.search(_string)
        if m:
            return (m.group(1),m.group(2))
        else:
            return ()

    def dump(self):
        print self.map
        

class CpuLoad(Parser):
    def __init__(self):
        Parser.__init__(self)
        self.type="syslog"
        self.regex = re.compile(r'(FSP-\d+|\w+Vm).*CPU [Ll]oad: (\d+)')

    def read(self):
        print "self.files: " + str(self.files)
        for filename in self.files:
            print "read filename : " + filename
            with open(filename) as f:
                for line in f:
                    values = Parser.search(self,line)
                    if(values!=()):
                        core=values[0]
                        load=values[1]
                        if core not in self.map:
                            self.map[core] = []
                        self.map[core].append(int(load))


class PdcpPacket(Parser):
    def __init__(self):
        Parser.__init__(self)
        self.type = "syslog"
        self.regex = re.compile(r'send (\d+) receive (\d+)')

    def read(self):
        for filename in self.files:
            with open(filename) as f:
                for line in f:
                    values = Parser.search(self,line)
                    if(values!=()):
                        send = values[0]
                        receive=values[1]
                        if 'send' not in self.map:
                            self.map['send'] = []
                        self.map['send'].append(int(send))
                        if 'receive' not in self.map:
                            self.map['receive'] = []
                        self.map['receive'].append(int(receive))

    def noReceived(self):
        return sum(element for element in self.map['receive'])

    def noSent(self):
        return sum(element for element in self.map['send'])

    def averageReceived(self):
        return PdcpPacket.noReceived(self)/len(self.map['receive'])

    def averageReceived(self):
        return PdcpPacket.noReceived(self)/len(self.map['send'])

import sys
import getopt

def usage():
    print "python test.py --application <application type> --board=<board type>"


def main(argv):
    inputfile=''
    application='syslogAnalyzer'
    board='fsm3'
    try:
        opts, args = getopt.getopt(argv,"hi:a:b:",["application=","board="])
    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-a", "--application"):
            application = arg
            if application not in ("syslogAnalyzer","eventAnalyzer","comparePerf"):
                print "wrong application: " + application
                sys.exit()
        elif opt in ("-b", "--board"):
            board = arg
            if board not in ("fsm3","fsm4","fsmr3","fsmr4","airscale","Airscale","dsp","arm","kepler"):
                print "wrong board type: " + board
                sys.exit()

    print '+'+'-'*60+'+'
    print "|{:<18}{:>2} {:<20}{:>20}".format("application type",":",application,"|")
    print "|{:<18}{:>2} {:<20}{:>20}".format("board type",":",board,"|")
    print '+'+'-'*60+'+'

    # check all files in results folder
    import os
    path  = "/home/quentin/Python/Parser/results"
    global files
    files = [path+"/"+filename for filename in os.listdir(path)]

    # parse cpu load data
    cpuload = CpuLoad()
    cpuload.read()
    cpuload.dump()

    #parse PDCP data
    pdcp = PdcpPacket()
    pdcp.read()
    pdcp.dump()
    print "received {} and sent {} PDPC packets".format(pdcp.noReceived(),pdcp.noSent())
    print pdcp.averageReceived()

if __name__ == "__main__":
    files=''
    main(sys.argv[1:])