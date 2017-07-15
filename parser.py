#!/usr/bin/python2.7

import re
from layers import *
#from pool import PoolStats
from csvWriter import Csv
import settings
from settings import Color,ProgressBar
import csv
#import ptime


def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1



class Check:
    def __init__(self):
        self.count     = 0
        self.extension = '.txt'
        self.type      = ''
        self.pattern   = ''

    def checkFile(self, path):
        fd = open(self.type + self.extension,'a')
        with open(path,'r') as f:
            for line in f:
                for pattern in self.patterns:
                    if re.search(r'{}'.format(pattern),line):
                        self.count += 1
                        fd.write(line)
        fd.close()

    def printResult(self):
        if self.count == 0:
            print Color.ok + "No {}".format(self.type) + Color.nocolor
        else:
            print "Number of {0:<7} : {1:}".format(self.type,self.count)
        

class Warning(Check):
    def __init__(self,path):
        Check.__init__(self)
        self.type     = 'warning'
        self.patterns = ['WRN','Warning','WARNING']
        self.checkFile(path)
        self.printResult()

class Error(Check):
    def __init__(self,path):
        Check.__init__(self)
        self.type     = 'error'
        self.patterns = ['ERR','error','ERROR']
        self.checkFile(path)
        self.printResult()

class Custom(Check):
    def __init__(self,path):
        Check.__init__(self)
        self.type     = "custom"
        self.patterns = ['long event detected']
        self.checkFile(path)
        self.printResult()


class Parser:
    def __init__(self):
        self.regex    = ''
        self.files    = settings.files
        self.regex    = None
        self.count    = 0

        self.srbSduData = 0
        self.receivedTBs = 0
        self.srbSdus = 0
        self.crcFails = 0
        self.msg3s = 0
        self.MacCEs = 0
        self.paddingData =0
        self.nokMacHeader = 0
        self.rlcPdus = 0
        self.drbSdus = 0
        self.lostUmPdus = 0

        self.discardedPdu = 0
        self.uplinkNack   = 0
        self.amPduSegments = 0
        self.nokRlcHeader = 0
        self.forwardedSdus = 0

        self.cpuload        = {}
        
        
        
        
       
    def search(self, parserType, _string):
        m = parserType.regex.search(_string)
        return (m.group(i+1) for i in range(parserType.count)) if m else ()



    '''
    def getCpuLoadStats(self,cpuload,line):
        cpuload.read()
        values = self.search(cpuload,line)
        if(values!=()):
            (core,timestamp,load,max)=values
            if core not in self.cpuload:
                self.cpuload[core] = []
            t = ptime.Time(timestamp)
            self.cpuload[core].append((t-0,float(load)))
    '''
        



    def printStatistics(self):
        print Color.bold + '   Other statistics:' + Color.nocolor
        pipe = Color.bold + "|" + Color.nocolor 
        print Color.bold + '+------------------------------------+-----------------------------------+' + Color.nocolor
        print Color.bold + '|          MAC                       |              RLC                  |' + Color.nocolor
        print Color.bold + '+------------------------------------+-----------------------------------+' + Color.nocolor
        print pipe + " total received TB      = {0:>8}  ".format(self.receivedTBs)  + pipe + "  total SRB SDUs        = {0:>8} ".format(self.srbSdus) + pipe
        print pipe + " total CRC failures     = {0:>8}  ".format(self.crcFails)     + pipe + "  total SRB SDU data    = {0:>8} ".format(self.srbSduData) + pipe
        print pipe + " total msg3s            = {0:>8}  ".format(self.msg3s)        + pipe + "  total UL NACK         = {0:>8} ".format(self.uplinkNack) + pipe
        print pipe + " total MAC CEs          = {0:>8}  ".format(self.MacCEs)       + pipe + "  total lost UM PDUs    = {0:>8} ".format(self.lostUmPdus) + pipe
        print pipe + " total paddingData      = {0:>8}  ".format(self.paddingData)  + pipe + "  total forwarded SDUs  = {0:>8} ".format(self.forwardedSdus) + pipe
        print pipe + " total NOK Mac Headers  = {0:>8}  ".format(self.nokMacHeader) + pipe + "  total AM PDU segments = {0:>8} ".format(self.amPduSegments) + pipe
        print pipe + " total RLC PDUs         = {0:>8}  ".format(self.rlcPdus)      + pipe + "  total NOK RLC Header  = {0:>8} ".format(self.nokRlcHeader) + pipe
        print pipe + " total DRB SDUs         = {0:>8}  ".format(self.drbSdus)      + pipe + "  total discarded PDU   = {0:>8} ".format(self.discardedPdu) + pipe
        print Color.bold + '+------------------------------------+-----------------------------------+' + Color.nocolor

    
'''
    def getUlPdcpThroughput(self):
        return self.ulpdcpthroughput

    def getRLCThroughput(self):
        return self.rlcthroughput

    def getUlRlcThroughput(self):
        return self.ulrlcthroughput

    def getMACThroughput(self):
        return self.macthroughput

    def getUlMacThroughput(self):
        return self.ulmacthroughput

    def getCpuLoad(self):
        return self.cpuload
        '''



class CpuLoad:
    def __init__(self):
        self.count = 0
        self.regex = None

    def read(self):
        self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.+)>.*CPU_Load=(\d+\.?\d*) max=(\d+\.?\d*)')
        self.count = 4



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
    path=''
    settings.png = False
    import getopt
    try:
        opts, args = getopt.getopt(argv,"hi:a:b:gw:cmp:v",["application=","board=","wcpy=","png","dpi=","show","clear"])
    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt == '-v':
            settings.verbose = True
        elif opt == '-g':
            graphAllowed = True
        elif opt in ('-w','--wcpy'):
            workPathNeeded = True
            branch = arg
        elif opt == '--dpi':
            graphAllowed = True
            settings.dpi = int(arg)
        elif opt == '--show':
            graphAllowed = True
            settings.showgraph = True
        elif opt == '--clear':
            settings.clear = True
        elif opt in ('-p'):
            path = arg
        elif opt in ("-i"):
            inputfile = arg
        elif opt in ("-a", "--application"):
            application = arg
            if application not in ("syslogAnalyzer","eventAnalyzer","comparePerf"):
                print "wrong application: " + application
                sys.exit()
        elif opt in("--png"):
            graphAllowed = True
            settings.png = True
        elif opt in ("-b", "--board"):
            board = arg
            if board not in ("fsm3","fsm4","fsmr3","fsmr4","airscale","Airscale","dsp","arm","kepler"):
                print "wrong board type: " + board
                sys.exit()
        elif opt == '-c':
            console = True

    
    # check all files in results folder
    import os
    if path =='':
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

    if (os.path.isfile('fileHistory.txt') and not settings.clear):
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
        
        if os.path.isfile('error.txt'):
            if settings.verbose : print "delete error.txt"
            os.remove('error.txt')
        if os.path.isfile('warning.txt'):
            if settings.verbose : print "delete warning.txt"
            os.remove('warning.txt')

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


        from datetime import datetime

        pdcppacket = PdcpPacket()
        #rlcpacket  = RlcPacket()
        #macpacket  = MacPacket()
        #cpuload    = CpuLoad()

        totalTime = datetime.now() 
        for filename in settings.files:
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

                        #self.getCpuLoadStats(cpuload,line)
                        pdcppacket.getPdcpThroughputFromLine(pdcppacket,line)
                        #self.getRlcThroughput(rlcpacket,line)
                        #self.getMacThroughput(macpacket,line)

                        #PHY stub
                        # CBitrate:: ... Kilobits pers second on CellId.. 
                    Bar.update(lineNumber,datetime.now() - d)
                Warning(filename)
                Error  (filename)
                Custom (filename)
        totalTime = datetime.now() - totalTime
        print "   \033[1mtotal time: {0:}:{1:02d}:{2:02d}.{3:03d}\033[0m\n".format(totalTime.seconds//3600,(totalTime.seconds//60)%60,totalTime.seconds,totalTime.microseconds/1000)




        createCsvThroughput('DL_PDCP',pdcppacket.getPDCPThroughput())
        #createCsvThroughput('UL_PDCP',parser.getUlPdcpThroughput())
        #createCsvThroughput('DL_RLC',parser.getRLCThroughput())
        #createCsvThroughput('UL_RLC',parser.getUlRlcThroughput())
        #createCsvThroughput('DL_MAC',parser.getMACThroughput())
        #createCsvThroughput('UL_MAC',parser.getUlMacThroughput())

        #createCsvLoad(parser.getCpuLoad())

    if (graphAllowed):
        import graph
        g = graph.Graph()
        if console:
            g.drawConsole('PDCP')
        else:
            g.drawFigure()

def getAllUeGroup(data):
    ueGroups = []
    for (timestamp,uegroup,value) in data:
        if uegroup not in ueGroups: ueGroups.append(uegroup)
    return ueGroups

def getValuesFromUeGroup(data,ref):
    values = []
    for (timestamp,uegroup,value) in data:
        if uegroup==ref: values.append(value)
    return values

def filtering(data):
    ueGroupToFilter = []
    ueGroups = getAllUeGroup(data)
    for uegroup in ueGroups:
        values = getValuesFromUeGroup(data,uegroup)
        if all(v<0.1 for v in values):
            ueGroupToFilter.append(uegroup)
    return ueGroupToFilter


def createCsv(name,type,data):
    if data == {}:
        print "\033[91mno data collected for {} {}\033[0m".format(name,type)
        return
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

        if 'MAC' in name or 'UL_RLC' in name:
            ueGroupToFilter = filtering(data[core])
            ueGroups=[]

            for (timestamp,ueGroup,throughput) in data[core]:
                if(ueGroup in ueGroupToFilter):
                    continue
                line = (timestamp,throughput)
                fd = 0 
                if ueGroup not in ueGroups:
                    ueGroups.append(ueGroup)
                    fd = open('csv/{}/{}_{}_{}_ueGroup{}.csv'.format(directory,name,type,core,ueGroup),'w')
                    writer = csv.writer(fd)
                    writer.writerow(header)
                else:
                    fd = open('csv/{}/{}_{}_{}_ueGroup{}.csv'.format(directory,name,type,core,ueGroup),'a')
                    writer = csv.writer(fd)
                writer.writerow(line)
                fd.close()
        else:
            if (all(e[1]<0.1 for e in data[core]) ):
                if settings.verbose: print "{}: data always 0.0 for core {} -> filtered".format(name,core)
                continue
            fd = open('csv/{}/{}_{}_{}.csv'.format(directory,name,type,core),'w')
            writer = csv.writer(fd)
            writer.writerow(header)
            for line in data[core]:
                writer.writerow(line)
            fd.close()
    print "CSV file created for {} {}".format(name,type)

def createCsvThroughput(layerName,data):
    createCsv(layerName,'throughput',data)

def createCsvLoad(data):
    createCsv('CPU','load',data)


if __name__ == "__main__":
    settings.init()
    main(sys.argv[1:])  
