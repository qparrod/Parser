#!/usr/bin/python2.7

import re

#filtrage in csv file
import csv


class Csv:
    def __init__(self):
        self.filename = ''
        self.mode     = ''

    def open(self, name):
        self.filename = name
        self.mode     = 'w'

    def write(self, fields, data):
        with open(self.filename,self.mode) as csvfile:
            writer = csv.DictWriter(csvfile,fieldnames=fields)
            writer.writeheader()
            for elements in data:
                writer.writerow(dict(zip(fields, elements)))



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


class RlcPacket():
    def __init__(self):
        self.count = 0

    def readRcvdRcvp(self):
        self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*RLC/STATS/DL: RCVD: (\d+ \d+ \d+) RCVP: (\d+ \d+ \d+) ACKD: (\d+ \d+ \d+) ACKP: (\d+ \d+ \d+)')
        self.count = 6


    def readBuffer(self):
        self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*RLC/STATS/DL: BuffPkt: (\d+ \d+ \d+) BuffData: (\d+ \d+ \d+)')
        self.count = 4


class PoolStats(Parser):
    def __init(self):
        Parser.__init(self)
        self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*STATS/EventPools: P: (\d+).*(\d*.?\d*)C: (\d+) LB: (\d+) L: (\d+) NB: (\d+).*(\d*).*(\d*).*(\d*).*(\d*).*(\d*)')  
        self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*STATS/SduPools: SRB:(\d+/\d+) SDU1:(\d+) SDU2:(\d+) .+ fully used:(\d*/\d*)')



class PdcpPacket(Parser):
    def __init__(self):
        Parser.__init__(self)
        self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*PDCP/STATS/DISCARD/DL: SDU: T (\d+ \d+ \d+) PDU: A (\d+ \d+ \d+) T (\d+ \d+ \d+)')
        self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*PDCP/STATS/DISCARD/DL: SR: (\d+) OOD: (\d+) OOM X2: (\d+) drb: (\d+) srb: (\d+) gtpu: (\d+)')
        self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*PDCP/STATS/DL: DRB S1: (\d+ \d+ \d+) X2: (\d+ \d+ \d+) inBytes: (\d+ \d+ \d+) toRLC: (\d+ \d+ \d+) inBytes: (\d+ \d+ \d+) ACK: (\d+ \d+ \d+) NACK: (\d+ \d+ \d+)')
        self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*PDCP/STATS/DL: SRB toRLC: (\d+ \d+ \d+) inBytes: (\d+ \d+ \d+) ACK: (\d+ \d+ \d+) NACK#1: (\d+ \d+ \d+) NACK#2: (\d+ \d+ \d+)')
        self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*PDCP/STATS/DL: BuffPkt: (\d+ \d+ \d+) BuffData: (\d+ \d+ \d+) Fwd: (\d+ \d+ \d+) SA SwQ/Tx/Rx: \d+/\d+/\d+ \d+/\d+/\d+ \d+/\d+/\d+ \[\d+\] WinStall: (\d+ \d+ \d+)')
        self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*PDCP/STATS/UL: DataPDU: (\d+ \d+ \d+) SR: (\d+) RoHCF: (\d+) toSGW: (\d+ \d+ \d+) Fwd: (\d+ \d+ \d+) BuffPkt: (\d+ \d+ \d+) BuffData: (\d+ \d+ \d+)')
        self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*DLUE STATS \d/.*1:(\d+) 2:(\d+) 3:(\d+) 4:(\d+) 5:(\d+) 6:(\d+) 7:(\d+)')
        self.regex = re.compile(r'8:(\d+) 9:(\d+) 10:(\d+)')
        self.count = 2

    def read(self):
        for filename in self.files:
            with open(filename) as f:
                for line in f:
                    values = Parser.search(self,line)
                    if(values!=()):
                        (send, receive) = values
                        if 'send' not in self.map:
                            self.map['send'] = []
                        self.map['send'].append(int(send))
                        if 'receive' not in self.map:
                            self.map['receive'] = []
                        self.map['receive'].append(int(receive))

    def noReceived(self):
        return sum(element for element in self.map['receive']) if 'receive' in self.map.keys() else 0

    def noSent(self):
        return sum(element for element in self.map['send']) if 'send' in self.map.keys() else 0

    def averageReceived(self):
        return PdcpPacket.noReceived(self)/len(self.map['receive']) if len(self.map['receive'])!= 0 else 0

    def averageReceived(self):
        return PdcpPacket.noReceived(self)/len(self.map['send']) if len(self.map['send'])!= 0 else 0

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
