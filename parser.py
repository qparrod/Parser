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
    
    def update(self, val, time):
        import sys
        perc  = int(round((float(val) / float(self.valmax)) * 100))
        scale = 100.0 / float(self.maxbar)
        bar   = int(perc / scale)
 
        if (perc!=100): 
            out = '\r{0} \033[1m {1:>3}%\033[0m [{2}{3}] time: {4:}:{5:02d}:{6:02d}.{7:03d}'.format(self.title,perc,'='*bar,' ' * (self.maxbar - bar),time.seconds//3600,(time.seconds//60)%60,time.seconds,time.microseconds/1000)
        else:
            out = '\r{0} \033[92m {1:>3}%\033[0m [{2}{3}] time: {4:}:{5:02d}:{6:02d}.{7:03d}'.format(self.title,perc,'='*bar,' ' * (self.maxbar - bar),time.seconds//3600,(time.seconds//60)%60,time.seconds,time.microseconds/1000) 

        sys.stdout.write(out)
        sys.stdout.flush()

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1
    

class Parser:
    def __init__(self):
        self.regex = ''
        self.files = settings.files
        self.regex = None
        self.count = 0
       
    def search(self,parserType, _string):
        m = parserType.regex.search(_string)
        return (m.group(i+1) for i in range(parserType.count)) if m else ()


    def read(self):
        rlcpacket  = RlcPacket()
        pdcppacket = PdcpPacket()
        macpacket = MacPacket()
        cpuload    = CpuLoad()

        cpuloadcsv = open('cpuload.csv','w')
        cpuloadwriter = csv.writer(cpuloadcsv)
        cpuloadwriter.writerow(['timestamp','core','load','max'])

        self.cpuload        = {}
        self.pdcpthroughput = {}
        self.rlcthroughput  = {}
        self.macthroughput  = {}
        
        totalTime = datetime.now() 
        for filename in self.files:
            if ( re.search(r'.*udplog_.*',filename) ):
                print "\nread filename : " + filename
                Bar = ProgressBar(file_len(filename),60, ' ')
                d = datetime.now()
                with open(filename) as f:
                    lineNumber=0
                    for line in f:
                        lineNumber=lineNumber+1
                        if (lineNumber%2000==0):
                            Bar.update(lineNumber,datetime.now() - d)

                        # CPU load
                        cpuload.read()
                        values = self.search(cpuload,line)
                        if(values!=()):
                            (core,timestamp,load,max)=values
                            if core not in self.cpuload:
                                self.cpuload[core] = []
                            self.cpuload[core].append((timestamp,float(load)))
                            cpuloadwriter.writerow([timestamp,core,load,max])
                          
                        # PDCP
                        pdcppacket.read()
                        values = self.search(pdcppacket,line)
                        if(values!=()):
                            (soc, core,timestamp, s1, x2, inbytes, toRlc, inbytesRLC, ack, nack) = values
                            [val1,val2,val3] = [int(s) for s in inbytes.split() if s.isdigit()]
                            if core not in self.pdcpthroughput:
                                self.pdcpthroughput[core] = []
                            self.pdcpthroughput[core].append((timestamp,val1*8/2.0/1024))
                            self.pdcpthroughput[core].append((timestamp,val2*8/2.0/1024))
                            self.pdcpthroughput[core].append((timestamp,val3*8/2.0/1024))
 
                        # RLC
                        rlcpacket.readRcvdRcvp()
                        values = self.search(rlcpacket,line)
                        if(values!=()):
                            (core,timestamp,rcvd,rcvp,ackd,ackp)=values
                            [val1,val2,val3] = [int(s) for s in rcvd.split() if s.isdigit()]
                            if core not in self.rlcthroughput:
                                self.rlcthroughput[core] = []
                            self.rlcthroughput[core].append((timestamp,val1*8/2.0/1024))
                            self.rlcthroughput[core].append((timestamp,val2*8/2.0/1024))
                            self.rlcthroughput[core].append((timestamp,val3*8/2.0/1024))

                        # MAC
                        macpacket.readReceivedData()
                        values = self.search(macpacket,line)
                        if(values!=()):
                            (core,timestamp,ueGroup,receivedData,receivedPackets,ackedData,ackedPacket,nackedData,nackedPacket,amountOfBufferedSdus,amountOfBufferedData,amountOfWastedMemory,lostBsrCount)=values
                            if (ueGroup == '0'):
                                if core not in self.macthroughput:
                                    self.macthroughput[core] = []
                                self.macthroughput[core].append((timestamp,int(receivedData)*8/2.0/1024))
                        

                        #PHY stub
                        # CBitrate:: ... Kilobits pers second on CellId.. 
                    Bar.update(lineNumber,datetime.now() - d)
        cpuloadcsv.close()
        totalTime = datetime.now() - totalTime
        print "\n   \033[1mtotal time: {0:}:{1:02d}:{2:02d}.{3:03d}\033[0m\n".format(totalTime.seconds//3600,(totalTime.seconds//60)%60,totalTime.seconds,totalTime.microseconds/1000)
        

    def getPDCPThroughput(self):
        return self.pdcpthroughput

    def getRLCThroughput(self):
        return self.rlcthroughput

    def getMACThroughput(self):
        return self.macthroughput

    def getCpuLoad(self):
        return self.cpuload



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
    graphAllowed = False
    workPathNeeded = False
    branch = ''
    try:
        opts, args = getopt.getopt(argv,"hi:a:b:gw:",["application=","board=","wcpy="])
    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt == '-g':
            graphAllowed = True
        elif opt in ('-w','--wcpy'):
            workPathNeeded = True
            branch = arg
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
    if not workPathNeeded:
        path = "/home/quentin/Python/Parser/results"
    else:
        user = os.getlogin()
        path = "/var/fpwork/"+ str(user) + "/"+branch+"/C_Test/SC_LTEL2/Sct/RobotTests/results"
    print "path=" + path

    import sys
    if sys.version_info < (2,7):
        print '\033[91m'+ 'must use python 2.7 or greater'
        print 'possible solution: use "seesetenv LINSEE_BTS-5.7.0" command' + '\033[0m'
        exit()

    for dirpath, dirnames, filenames in os.walk(path):
        if(dirnames!=[]):
            emTrace='activated'
            emTraceFolderName = dirnames[0]
        settings.files = [os.path.join(dirpath,name) for name in filenames]
        break
   
    nofiles = len(settings.files) 
    if (nofiles==0):
        print '\033[91m' + "no file in path" + '\033[0m'
        exit();
    print "number of files in path: {0}".format(nofiles)

    settings.files.sort()

    udplognb = 0
    for filename in settings.files:
        if ( re.search(r'.*udplog_.*',filename) ):
            udplognb=udplognb+1
    print "number of udplog files in path: {}".format(udplognb)

    csvDirectory='csv'
    directory=csvDirectory
    if os.path.exists(directory):
        import shutil
        shutil.rmtree(directory)
    os.makedirs(directory)

    throughputDirectory='throughput'
    cpuloadDirectory='cpuload'
    os.makedirs(directory+'/'+throughputDirectory)
    os.makedirs(directory+'/'+cpuloadDirectory)

    ## check board type and deployment from startup log
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
                        
    print '\033[1m'+'+'+'-'*60+'+'
    print "|{0:<18}{1:>2} {2:<20}{3:>20}".format("application type",":",application,"|")
    if (cloud): print "|{0:<18}{1:>2} {2:<20}{3:>20}".format("environment",":",'cloud',"|")
    print "|{0:<18}{1:>2} {2:<20}{3:>20}".format("board type",":",board,"|")
    print "|{0:<18}{1:>2} {2:<20}{3:>20}".format("deployment",":",deployment,"|")
    print '+'+'-'*60+'+' + '\033[0m'

    parser=Parser()
    parser.read()

    createCsvThroughput('PDCP',parser.getPDCPThroughput())
    createCsvThroughput('RLC',parser.getRLCThroughput())
    createCsvThroughput('MAC',parser.getMACThroughput())

    createCsvLoad(parser.getCpuLoad())

    if (graphAllowed):
        import time
        import datetime

        data = parser.getPDCPThroughput()

        ex = [ pair[1] for pair in data["LINUX-Disp_0"] ]
        t = [ time.mktime(datetime.datetime.strptime(pair[0], "%Y-%m-%dT%H:%M:%S.%fZ").timetuple()) for pair in data["LINUX-Disp_0"] ]

        import graph
        graph.draw(zip(ex,t))



def createCsv(name,type,data):
    #if name=='MAC': print data
    for core in data:
        directory = ''
        header= []
        if (type=="throughput"):
            directory = 'throughput'
            header = ['timestamp','{} {} in kbps for core {}'.format(name,type,core)]
        elif (type=="load"):
            directory = 'cpuload'
            header = ['timestamp','{} {} in % for core {}'.format(name,type,core)]
        else:
            print "csv file type not recognized"
            exit()
        fd = open('csv/{}/{}_{}_{}.csv'.format(directory,name,type,core),'w')
        writer = csv.writer(fd)
        writer.writerow(header)
        for line in data[core]:
            writer.writerow(line)
        fd.close()

def createCsvThroughput(layerName,data):
    createCsv(layerName,'throughput',data)

def createCsvLoad(data):
    createCsv('CPU','load',data)


if __name__ == "__main__":
    settings.init()
    main(sys.argv[1:])  
