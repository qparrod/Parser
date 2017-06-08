#!/usr/bin/python2.7

import re
from layers import *
from csvWriter import Csv
import settings
import csv
from datetime import datetime

class ProgressBar:
    def __init__ (self, valmax, maxbar, title):
        if valmax == 0:  valmax = 1
        if maxbar > 200: maxbar = 200
        self.valmax = valmax
        self.maxbar = maxbar
        self.title  = title
    
    def update(self, val, seconds):
        import sys
        perc  = int(round((float(val) / float(self.valmax)) * 100))
        scale = 100.0 / float(self.maxbar)
        bar   = int(perc / scale)
  
        out = '\r{0}  {1:>3}% [{2}{3}] {4:>6}/{5:>6}   | ETA: {6:}s'.format(self.title,perc,'='*bar,' ' * (self.maxbar - bar),val,self.valmax,seconds)
        sys.stdout.write(out)
        sys.stdout.flush()

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1
    

class Parser:
    def __init__(self):
        self.regex=''
        self.type=""
        self.files = settings.files
        self.regex = None
        self.count = 0
        self.pdcpthroughput = []
       
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
        pdcpcsv1 = open('pdcp1.csv','w')
        cpuloadwriter = csv.writer(cpuloadcsv)
        pdcp1writer = csv.writer(pdcpcsv1)
        cpuloadwriter.writerow(['timestamp','core','load','max'])
        pdcp1writer.writerow(['timestamp','core','s1','x2','bytes','ACK','NACK'])
        # warning : sort self.files depending on filename timestamp
        for filename in self.files:
            if ( re.search(r'.*udplog_.*',filename) ):
                print "\nread filename : " + filename
                Bar = ProgressBar(file_len(filename),60, ' ')
                d = datetime.now()
                with open(filename) as f:
                    lineNumber=0
                    for line in f:
                        lineNumber=lineNumber+1
                        if (lineNumber%250==0):
                            delta = datetime.now() - d
                            seconds = int(delta.total_seconds())
                            Bar.update(lineNumber,seconds)

                        # CPU load
                        cpuload.read()
                        values = self.search(cpuload,line)
                        if(values!=()):
                            (core,timestamp,load,max)=values
                            if core not in self.cpuloadMap:
                                self.cpuloadMap[core] = [()]
                            self.cpuloadMap[core].append((timestamp,float(load)))
                            cpuloadwriter.writerow([timestamp,core,load,max])
                          
                        # PDCP
                        pdcppacket.read()
                        values = self.search(pdcppacket,line)
                        if(values!=()):
                            (soc, core,timestamp, s1, x2, inbytes, toRlc, inbytesRLC, ack, nack) = values
                            [test2,test4,test6] = [int(s) for s in inbytes.split() if s.isdigit()]
                            pdcp1writer.writerow([timestamp,soc,s1,x2,inbytes,ack,nack])
                            if (core=='LINUX-Disp_1'):
                                throughput2s = test2*8/2.0/1024.0 # kbps
                                throughput4s = test4*8/2.0/1024.0
                                throughput6s = test6*8/2.0/1024.0
                                self.pdcpthroughput.append(throughput2s)
                                self.pdcpthroughput.append(throughput4s)
                                self.pdcpthroughput.append(throughput6s)
 
                        # RLC
                        rlcpacket.readRcvdRcvp()
                        values = self.search(rlcpacket,line)
                        if(values!=()):
                            (core,timestamp,rcvd,rcvp,ackd,ackp)=values
                            if core not in self.rlcMap:
                                self.rlcMap[core] = [()]
                            self.rlcMap[core].append("rcvd:" + rcvd)

                        # MAC

                        #PHY stub
                        # CBitrate:: ... Kilobits pers second on CellId.. 

                    seconds = int(delta.total_seconds())
                    Bar.update(lineNumber,seconds)
        cpuloadcsv.close()

    def dump(self):
        print "\ndump CPU load information:"
        print self.cpuloadMap
        print "\ndump RLC information:"
        print self.rlcMap
        #print "\ndump PDCP information:"
        #print self.pdcpMap

    def dumpThroughput(self):
        print self.pdcpthroughput

    def getPDCPThroughput(self):
        return self.pdcpthroughput

    def getRLCThroughput(self):
        return self.rlcthroughput

    def getMACThroughput(self):
        return self.macthroughput

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

    udplognb = 0
    for filename in settings.files:
        if ( re.search(r'.*udplog_.*',filename) ):
            udplognb=udplognb+1
    print "number of udplog files in path: {}".format(udplognb)
#from logs:
    ## 1/check board type
    cloud = False
    for filename in settings.files:
        if ( re.search(r'.*udplog_Node_startup_.*',filename) ):
            with open(filename,'r') as f:
                for line in f:
                    if(re.search(r'VM-\d+.+',line)): cloud=True
                    m = re.search(r'Detected module (.*) and',line)
                    if (m): board = m.group(1)
                    m = re.search(r'Cpu\d Idling! (\dDSP) ',line)
                    if (m): deployment = m.group(1)
            break
                        

    print '\033[1m'
    print '+'+'-'*60+'+'
    print "|{0:<18}{1:>2} {2:<20}{3:>20}".format("application type",":",application,"|")
    if (cloud): print "|{0:<18}{1:>2} {2:<20}{3:>20}".format("environment",":",'cloud',"|")
    print "|{0:<18}{1:>2} {2:<20}{3:>20}".format("board type",":",board,"|")
    print "|{0:<18}{1:>2} {2:<20}{3:>20}".format("deployment",":",deployment,"|")
    print '+'+'-'*60+'+'
    print '\033[0m'

    

    ## 2/check deployment

    # parse cpu load data
    #cpuload = CpuLoad()
    #cpuload.read()
    #cpuload.dump()

    #TODO : read throughput on UeVm side (PDCP, RLC) to see bottlenecks
    #       -> need to understand logs stats
    parser=Parser()
    parser.read()
    #parser.dump()
    parser.dumpThroughput()

    throughput = parser.getPDCPThroughput()
    pdcpthoughput =  open('throughput.csv','w')
    pdcpthroughputwriter = csv.writer(pdcpthoughput)
    pdcpthroughputwriter.writerow(['throughput in kbps'])
    pdcpthroughputwriter.writerow(['PDCP,RLC,MAC'])
    for tput in throughput:
        pdcpthroughputwriter.writerow([tput])
    pdcpthoughput.close()
    

    #create csv files
    docsv = Csv()
    docsv.open('data.csv')
    fields = ['ex1','ex2','ex3']
    data = [[1,2,3],[4,5,6],[7,8,9],[10,11,12]]
    docsv.write(fields,data)

    # plot graphs here no matplot lib on LINSEE
    
    print "\n"

if __name__ == "__main__":
    settings.init()
    main(sys.argv[1:])  
