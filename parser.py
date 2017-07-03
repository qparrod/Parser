#!/usr/bin/python2.7

import re
from layers import *
from csvWriter import Csv
import settings
import csv


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
 
        color = ''

        if (perc!=100): color = '\033[1m'
        else:           color = '\033[92m'

        out = '\r{0} {1} {2:>3}%\033[0m [{3}{4}] time: {5:}:{6:02d}:{7:02d}.{8:03d}'.format(self.title,color,perc,'='*bar,' ' * (self.maxbar - bar),
            time.seconds//3600,(time.seconds//60)%60,time.seconds,time.microseconds/1000) 

        sys.stdout.write(out)
        sys.stdout.flush()

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def fromBitToByte(val):
    return int(val / 8)

def fromByteToBit(val):
    return val * 8


import ptime
    

class Parser:
    def __init__(self):
        self.regex    = ''
        self.files    = settings.files
        self.regex    = None
        self.count    = 0
        self.ueGroups = []
       
    def search(self, parserType, _string):
        m = parserType.regex.search(_string)
        return (m.group(i+1) for i in range(parserType.count)) if m else ()

    def getPdcpThroughput(self,pdcppacket,line):
        pdcppacket.read()
        values = self.search(pdcppacket,line)
        if(values!=()):
            (soc, core,timestamp, s1, x2, inbytes, toRlc, inbytesRLC, ack, nack) = values
            values = [int(s) for s in inbytes.split() if s.isdigit()]
            if core not in self.pdcpthroughput:
                self.pdcpthroughput[core] = []
            t = ptime.Time(timestamp)
            timeDelta = 2.0 # 2 seconds between traces
            for i in reversed(range(len(values))):
                self.pdcpthroughput[core].append((t-timeDelta*i,fromByteToBit(values[len(values)-1-i])/timeDelta/1024))


    def getRlcThroughput(self,rlcpacket,line):
        rlcpacket.readRcvdRcvp()
        values = self.search(rlcpacket,line)
        if(values!=()):
            (core,timestamp,rcvd,rcvp,ackd,ackp)=values
            values = [int(s) for s in rcvd.split() if s.isdigit()]
            if core not in self.rlcthroughput:
                self.rlcthroughput[core] = []
            t = ptime.Time(timestamp)
            timeDelta = 2.0 # 2 seconds between traces
            for i in reversed(range(len(values))):
                self.rlcthroughput[core].append((t-timeDelta*i,fromByteToBit(values[len(values)-1-i])/timeDelta/1024))

    def getMacThroughput(self,macpacket,line):
        macpacket.readReceivedData()
        values = self.search(macpacket,line)
        if(values!=()):
            (core,timestamp,ueGroup,receivedData,receivedPackets,ackedData,ackedPacket,nackedData,nackedPacket,amountOfBufferedSdus,amountOfBufferedData,amountOfWastedMemory,lostBsrCount)=values
            if ueGroup not in self.ueGroups:
                self.ueGroups.append(ueGroup)
            if (ueGroup == '0'): #TODO : generalize this
                if core not in self.macthroughput:
                    self.macthroughput[core] = []
                t = ptime.Time(timestamp)
                self.macthroughput[core].append((t-0,fromByteToBit(int(receivedData))/2.0/1024))

    def getCpuLoadStats(self,cpuload,line):
        cpuload.read()
        values = self.search(cpuload,line)
        if(values!=()):
            (core,timestamp,load,max)=values
            if core not in self.cpuload:
                self.cpuload[core] = []
            t = ptime.Time(timestamp)
            self.cpuload[core].append((t-0,float(load)))


    def read(self):
        from datetime import datetime

        rlcpacket  = RlcPacket()
        pdcppacket = PdcpPacket()
        macpacket = MacPacket()
        cpuload    = CpuLoad()

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

                        self.getCpuLoadStats(cpuload,line)
                        self.getPdcpThroughput(pdcppacket,line)
                        self.getRlcThroughput(rlcpacket,line)
                        self.getMacThroughput(macpacket,line)

                        #PHY stub
                        # CBitrate:: ... Kilobits pers second on CellId.. 
                    Bar.update(lineNumber,datetime.now() - d)
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
    def __init__(self):
        Parser.__init__(self)
        self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*STATS/EventPools: P: (\d+).*(\d*.?\d*)C: (\d+) LB: (\d+) L: (\d+) NB: (\d+).*(\d*).*(\d*).*(\d*).*(\d*).*(\d*)')  
        self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*STATS/SduPools: SRB:(\d+/\d+) SDU1:(\d+) SDU2:(\d+) .+ fully used:(\d*/\d*)')


import sys

def usage():
    print "python test.py --application <application type> --board=<board type>"


def main(argv):
    ResultFolderAlreadyRead = False
    inputfile=''
    application='syslogAnalyzer'
    board='fsm3'
    deployment = 'cloud fsm3 6dsp'
    graphAllowed = False
    workPathNeeded = False
    console=False
    branch = ''
    import getopt
    try:
        opts, args = getopt.getopt(argv,"hi:a:b:gw:cm",["application=","board=","wcpy="])
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
        elif opt == '-c':
            console = True

    
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

    if (os.path.isfile('fileHistory.txt')):
        fileHistory = open('fileHistory.txt','r')
        print "open history files"
        ResultFolderAlreadyRead = True
        for line in fileHistory:
            line = line.rstrip('\n')
            found = False
            for e in settings.files:
                if line == e:
                    found = True;
                    break
            if(not found):
                ResultFolderAlreadyRead = False

        fileHistory.close()

    print "Result already read: {}".format(ResultFolderAlreadyRead)


    if not ResultFolderAlreadyRead : 
        fileHistory = open('fileHistory.txt','w')
        udplognb = 0
        for filename in settings.files:
            if ( re.search(r'.*udplog_.*',filename) ):
                udplognb=udplognb+1
                fileHistory.write(filename+'\n')
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
        import graph
        g = graph.Graph()
        if console:
            g.drawConsole('PDCP')
        else:
            g.drawFigure()



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
