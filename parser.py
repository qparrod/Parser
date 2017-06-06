#!/usr/bin/python2.7

import re
import pdcp
from csvWriter import Csv


class Parser:
    def __init__(self):
        global files
        self.regex=''
        self.type=""
        self.files = files
        self.regex = None
        self.count = 0
       
    def search(self,parser, _string):
        m = parser.regex.search(_string)
        return (m.group(i+1) for i in range(parser.count)) if m else ()


    def read(self):
        rlcpacket = RlcPacket()
        self.rlcMap  = {}
        self.pdcpMap = {}
        cpuload = CpuLoad()
        self.cpuloadMap = {}
        for filename in self.files:
            if ( re.search(r'.*udplog_.*',filename) ):
                print "read filename : " + filename
                with open(filename) as f:
                    for line in f:
                        cpuload.read()
                        values = self.search(cpuload,line)
                        if(values!=()):
                            (core,timestamp,load,max)=values
                            if core not in self.cpuloadMap:
                                self.cpuloadMap[core] = [()]
                            self.cpuloadMap[core].append((timestamp,float(load)))

                        rlcpacket.readRcvdRcvp()
                        values = self.search(rlcpacket,line)
                        if(values!=()):
                            (core,timestamp,rcvd,rcvp,ackd,ackp)=values
                            if core not in self.rlcMap:
                                self.rlcMap[core] = [()]
                            self.rlcMap[core].append("rcvd:" + rcvd)


    def dump(self):
        print "\ndump CPU load information:"
        print self.cpuloadMap
        print "\ndump RLC information:"
        print self.rlcMap
        #print "\ndump PDCP information:"
        #print self.pdcpMap



class CpuLoad():
    def __init__(self):
        self.count = 0
        self.regex = None

    def read(self):
        self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.+)>.*CPU_Load=(\d+\.?\d*) max=(\d+\.?\d*)')
        self.count = 4





class PoolStats(Parser):
    def __init(self):
        Parser.__init(self)
        self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*STATS/EventPools: P: (\d+).*(\d*.?\d*)C: (\d+) LB: (\d+) L: (\d+) NB: (\d+).*(\d*).*(\d*).*(\d*).*(\d*).*(\d*)')  
        self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*STATS/SduPools: SRB:(\d+/\d+) SDU1:(\d+) SDU2:(\d+) .+ fully used:(\d*/\d*)')





import sys
import getopt

def usage():
    print "python test.py --application <application type> --board=<board type>"


def main(argv):
    inputfile=''
    application='syslogAnalyzer'
    board='fsm3'
    deployment = 'cloud fsm3 6dsp'
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
    print "|{:<18}{:>2} {:<20}{:>20}".format("deployment",":",deployment,"|")
    print '+'+'-'*60+'+'

    # check all files in results folder
    import os

    path = "/home/quentin/Python/Parser/results"
    user = os.environ['USER']
    #user = os.getlogin()
    #path = "/var/fpwork/"+ str(user) + "/FTL2/C_Test/SC_LTEL2/Sct/RobotTests/results"
    print path
    global files
    #files = [path+"/"+filename for filename in os.listdir(path)]
    for dirpath, dirnames, filenames in os.walk(path):
        if(dirnames!=[]):
            emTrace='activated'
            emTraceFolderName = dirnames[0]
            files = [os.path.join(dirpath,name) for name in filenames]
        break

#from logs:
    ## 1/check board type
    ## 2/check deployment

    # parse cpu load data
    #cpuload = CpuLoad()
    #cpuload.read()
    #cpuload.dump()

    #TODO : read throughput on UeVm side (PDCP, RLC) to see bottlenecks
    #       -> need to understand logs stats
    #pdcp = PdcpPacket()
    #pdcp.read()
    #pdcp.dump()
    #print "received {} and sent {} PDPC packets".format(pdcp.noReceived(),pdcp.noSent())
    #print pdcp.averageReceived()

    parser=Parser()
    parser.read()
    parser.dump()
    #rlc = RlcPacket()
    #rlc.readBuffer()
    #rlc.dump()

    #create csv files
    docsv = Csv()
    docsv.open('data.csv')
    fields = ['ex1','ex2','ex3']
    data = [[1,2,3],[4,5,6],[7,8,9],[10,11,12]]
    docsv.write(fields,data)

    # plot graphs here no matplot lib on LINSEE


if __name__ == "__main__":
    files=''
    main(sys.argv[1:])  
