#!/usr/bin/python2.7

import re
from layers import *
from csvWriter import Csv
import settings
import csv

class ProgressBar:
    '''
    Progress bar
    '''
    def __init__ (self, valmax, maxbar, title):
        if valmax == 0:  valmax = 1
        if maxbar > 200: maxbar = 200
        self.valmax = valmax
        self.maxbar = maxbar
        self.title  = title
    
    def update(self, val):
        import sys
        # process
        perc  = round((float(val) / float(self.valmax)) * 100)
        scale = 100.0 / float(self.maxbar)
        bar   = int(perc / scale)
  
        # render 
        out = '\r %s [%s%s] %3d %%' % (self.title, '=' * bar, ' ' * (self.maxbar - bar), perc)
        sys.stdout.write(out)
        sys.stdout.flush()

class Parser:
    def __init__(self):
        self.regex=''
        self.type=""
        self.files = settings.files
        self.regex = None
        self.count = 0
       
    def search(self,parserType, _string):
        m = parserType.regex.search(_string)
        return (m.group(i+1) for i in range(parserType.count)) if m else ()


    def read(self):
        rlcpacket = RlcPacket()
        self.rlcMap  = {}
        pdcppacket = PdcpPacket()
        self.pdcpMap = {}
        cpuload = CpuLoad()
        self.cpuloadMap = {}
        cpuloadcsv = open('cpuload.csv','w')
        for filename in self.files:
            if ( re.search(r'.*udplog_.*',filename) ):
                print "read filename : " + filename
                Bar = ProgressBar(100, 60, '')
                for i in xrange(100):
                    Bar.update(i)
                with open(filename) as f:
                    for line in f:
                        cpuload.read()
                        values = self.search(cpuload,line)
                        if(values!=()):
                            (core,timestamp,load,max)=values
                            if core not in self.cpuloadMap:
                                self.cpuloadMap[core] = [()]
                            self.cpuloadMap[core].append((timestamp,float(load)))
                            cpuloadwriter = csv.writer(cpuloadcsv)
                            cpuloadwriter.writerow(['timestamp','core','load','max'])
                            cpuloadwriter.writerow([timestamp,core,load,max])
                            
                        pdcppacket.read()
                        values = self.search(pdcppacket,line)
                        if(values!=()):
                            (core, timestamp, s1, x2, send, receive, a, a, a) = values
                            if 'send' not in self.pdcpMap:
                                self.pdcpMap['send'] = []
                            #self.pdcpMap['send'].append(int(send))
                            if 'receive' not in self.pdcpMap:
                                self.pdcpMap['receive'] = []
                            #self.pdcpMap['receive'].append(int(receive))                       
 
                        rlcpacket.readRcvdRcvp()
                        values = self.search(rlcpacket,line)
                        if(values!=()):
                            (core,timestamp,rcvd,rcvp,ackd,ackp)=values
                            if core not in self.rlcMap:
                                self.rlcMap[core] = [()]
                            self.rlcMap[core].append("rcvd:" + rcvd)
        cpuloadcsv.close()

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
    
    print '\033[1m'
    print '+'+'-'*60+'+'
    print "|{0:<18}{1:>2} {2:<20}{3:>20}".format("application type",":",application,"|")
    print "|{0:<18}{1:>2} {2:<20}{3:>20}".format("board type",":",board,"|")
    print "|{0:<18}{1:>2} {2:<20}{3:>20}".format("deployment",":",deployment,"|")
    print '+'+'-'*60+'+'
    print '\033[0m'

    # check all files in results folder
    import os

    #path = "/home/quentin/Python/Parser/results"
    user = os.environ['USER']
    #user = os.getlogin()
    path = "/var/fpwork/"+ str(user) + "/FTL2/C_Test/SC_LTEL2/Sct/RobotTests/results"
    print "path=" + path
    #files = [path+"/"+filename for filename in os.listdir(path)]
    for dirpath, dirnames, filenames in os.walk(path):
        if(dirnames!=[]):
            emTrace='activated'
            emTraceFolderName = dirnames[0]
        settings.files = [os.path.join(dirpath,name) for name in filenames]
        break
    
    print "number of files in path: {}".format(len(settings.files))
    if (len(settings.files)==0):
        print '\033[91m' + "no file in path" + '\033[0m'
        exit();

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
    settings.init()
    main(sys.argv[1:])  
