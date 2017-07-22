#!/usr/bin/python2.7

import re
from layers import *
#from pool import PoolStats
import settings
from settings import Color,ProgressBar
from csvWriter import *


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
            print Color.ok + "   No {}".format(self.type) + Color.nocolor
        else:
            print "   Number of {0:<7} : {1:}".format(self.type,self.count)
    
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

    timeDelta = 2.0

    def __init__(self):
        self.regex    = ''
        self.files    = settings.files
        self.regex    = None
        self.count    = 0
        self.line     = ''

    def search(self):
        m = self.regex.search(self.line)
        return [ m.group(i+1) for i in range(self.count) ] if m else ()

    def search2(self):
        m = self.regex.search(self.line)
        return [ m.group(i+1) for i in range(self.count) ] if m else ('','',None)


    def fromByteToBit(self,val):
        return val * 8

    def convertToKbps(self,val):
        return val / 1024

    def get(self, pos):
        import ptime
        values = self.search()
        if values != () :
            if pos == 4:
                print self.line
            core      = values[0]
            timestamp = values[1]
            data      = values[pos]
            values = [ int(s) for s in data.split() if s.isdigit() ]
            if core not in self.data:
                self.data[core] = []
            t = ptime.Time(timestamp)
            timeDelta = 2.0
            for i in reversed(range(len(values))):
                timeInDatetime   = t - i * Parser.timeDelta
                throughputInkbps = self.convertToKbps(self.fromByteToBit(values[len(values)-1-i])/Parser.timeDelta)
                return (timeInDatetime, throughputInkbps)
                #self.data[core].append( (timeInDatetime, throughputInkbps) )
        else :
            return None

    def calculateThroughput(self):
        self.value = [ int(v) * 8 / 1024  / 2.0  for v in self.value ] # in kbps


    def get2(self,regex):
        import ptime
        self.regex = re.compile(r'(LINUX-Disp_\d) <(.*)>.*'+regex)
        self.count = 3 # core, timestamp and value
        core, timestamp, data = self.search2()
        values = [ int(s) for s in data.split() if s.isdigit() ] if data else []
        t = ptime.Time(timestamp)
        timeDelta = 2.0

        timeInDatetime = []
        throughputInkbps = []
        for i in reversed(range(len(values))):
            timeInDatetime.append( t - i * Parser.timeDelta )
            #throughputInkbps.append( self.convertToKbps(self.fromByteToBit(values[len(values)-1-i])/Parser.timeDelta) )
        return core, timeInDatetime, values



class CpuLoad(Parser):
    def __init__(self):
        Parser.__init__(self)
        self.cpuload = {} 

    def read(self):
        self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.+)>.*CPU_Load=(\d+\.?\d*) max=(\d+\.?\d*)')
        self.count = 4

    def getCpuLoad(self):
        return self.cpuload

    def getCpuLoadStats(self,line):
        self.read()
        self.line = line
        values = self.search()
        if(values!=()):
            (core,timestamp,load,max)=values
            if core not in self.cpuload:
                self.cpuload[core] = []
            t = ptime.Time(timestamp)
            self.cpuload[core].append((t-0,float(load)))

def getGlobalInformation():
    found = False
    for filename in settings.files:
        if ( re.search(r'.*udplog_Node_startup_.*',filename) ):
            found = True
            with open(filename,'r') as f:
                for line in f:
                    if(re.search(r'VM-\d+.+',line)): settings.cloud=True
                    m = re.search(r'Detected module (.*) and',line)
                    if (m): settings.board = m.group(1)
                    m = re.search(r'Cpu\d Idling! (\dDSP) ',line)
                    if (m): settings.deployment = m.group(1)
            break
    if not found:
         print Color.warning + "File containing deployment and board not found (udplog_Node_startup...)" + Color.nocolor

def printGlobalInformation():
    print '\033[1m'+'+'+'-'*60+'+'
    print "|{0:<18}{1:>2} {2:<20}{3:>20}".format("application type",":",settings.application,"|")
    if (settings.cloud): print "|{0:<18}{1:>2} {2:<20}{3:>20}".format("environment",":",'cloud',"|")
    print "|{0:<18}{1:>2} {2:<20}{3:>20}".format("board type",":",settings.board,"|")
    print "|{0:<18}{1:>2} {2:<20}{3:>20}".format("deployment",":",settings.deployment,"|")
    print '+'+'-'*60+'+' + '\033[0m'

def checkVersion():
    import sys
    if sys.version_info < (2,7):
        print Color.error + 'must use python 2.7 or greater'
        print 'possible solution: use "seesetenv LINSEE_BTS-5.7.0" command' + Color.nocolor
        exit()

def usage():
    print Color.underline + "Usage" + Color.nocolor + " :"
    print "$ python2.7 {} --application <application type> --board=<board type>".format(settings.programName)
    print "options:"
    print "   -h|--help          show this usage"
    print "   -v                 verbose mode"
    print "   -w|--wcpy          set working copy name e.g /var/fpwork/user/<wcpy_name>/C_Test/SC_LTEL2/Sct/RobotTests/results"
    print "   -t|--type          set syslog type. SyslogAnalyzer will check all file with this type in filename. By default set to 'udplog'"
    print "                      This could be also a file extension. For instance '.log' or '.txt'"
    print "   -p|--path          instead of following working copy folder with -w option, this parameter set all path e.g /path/to/result/folder"
    print "   -g                 enable graphical mode which open figures"
    print "   -c                 show graphs on console. Need -g option."
    print "   --show             show figure in a new window. Need -g option"
    print "   -a|--application   choose tool to use. syslogAnalyzer by default which analysis udplogs"
    print "   -b|--board         select which product to use. (fsmr3, Airscale...)"
    print "   --cloud            specify that logs are in cloud environment. Useful whenNode_startup file is not present"
    print "   --clear            by default file analysis is stored in CSV file. If script is run again, this will regenarated analysis and CSV files"
    print "   --png              enable creation of PNG image of figures. Need -g option"
    print "   --dpi              set DPI (dots per inch) for image. Need -g option"
    print "\nExample:\n python parser.py -v -p /home/user/project/result -g --clear --png --dpi 50 "
    print " will analyse syslogs from /home/user/project/result folder and created a figure and saved it in a png image of dpi 50"

def getArguments(argv):
    import sys
    import getopt
    try:
        opts, args = getopt.getopt(argv,"hi:a:b:gw:cmp:vt:",["application=","board=","wcpy=","png","dpi=","show","clear","type","path","cloud"])
    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt == '-v':
            settings.verbose      = True
        elif opt == '-g':
            settings.graphAllowed = True
        elif opt in ('-w','--wcpy'):
            settings.workPathNeeded        = True
            settings.branch       = arg
        elif opt == '--dpi':
            settings.graphAllowed = True
            settings.dpi          = int(arg)
        elif opt == '--show':
            settings.plot         = True
        elif opt == '--clear':
            settings.clear        = True
        elif opt == '--cloud':
            settings.cloud        = True
        elif opt in ('-p', "--path"):
            settings.path         = arg
        elif opt in ('-t', "--type"):
            settings.syslogType   = arg
        elif opt in ("-a", "--application"):
            settings.application  = arg
            if settings.application not in ("syslogAnalyzer","eventAnalyzer","comparePerf"):
                print Color.error + "wrong application: " + settings.application + Color.nocolor
                sys.exit()
        elif opt in("--png"):
            settings.graphAllowed = True
            settings.png          = True
        elif opt in ("-b", "--board"):
            settings.board        = arg
            if settings.board not in ("fsm3","fsm4","fsmr3","fsmr4","airscale","Airscale","dsp","arm","kepler"):
                print "wrong board type: " + settings.board
                sys.exit()
        elif opt == '-c':
            settings.console = True

def printSelectedArguments():
    if settings.verbose:
        print "option selected :"
        print "    verbose mode activated (-v)"
        if settings.clear : print "    regenerating CSV file selected (--clear)"
        if settings.graphAllowed : print "    graph generation selected (-g or --show)"
        if settings.branch != '' : print "    working {} copy selected (-w)".format(settings.branch)
        if settings.png : print "    PNG image to create (--png)"
        if settings.syslogType != 'udplog' : print "    file type is {} (-t)".format(settings.syslogType)
        else : print "    file type is udplog [default]"
        if settings.graphAllowed and settings.dpi != 50  : print "    DPI set to {} (--dpi)".format(settings.dpi)
        elif settings.graphAllowed and settings.dpi == 50 : print "    DPI set to 50 [default]"
        if settings.path !='' : print "    path '{}'' selected (-p)".format(settings.path)
        if settings.graphAllowed and settings.console : print "    graph will be displayed on console (-c)"


def isFolderAlreadyAnalyzed():
    import os
    ResultFolderAlreadyRead = True
    if settings.verbose : print "Checking if result folder has already been checked"
    if os.path.isfile('fileHistory.txt') :
        fileHistory = open('fileHistory.txt','r')
        if settings.verbose : print "open history files"
        for line in fileHistory:
            line  = line.rstrip('\n')
            found = False
            for filename in settings.files:
                if line == filename:
                    found = True;
                    break
            if(not found):
                ResultFolderAlreadyRead = False
        fileHistory.close()
    if settings.verbose : print "Result already read: {}".format(ResultFolderAlreadyRead)
    return ResultFolderAlreadyRead and not settings.clear

def checkFileNumber():
    if settings.verbose : print "checking file number..."
    nofiles = len(settings.files) 
    if (nofiles==0):
        print Color.error + "no file in path" + Color.nocolor
        exit();
    if settings.verbose : print "number of files in path: {}".format(nofiles)

def checkFileType():
    count = 0
    for filename in settings.files:
        if settings.syslogType in filename:
            count += 1
    if count != 0 : 
        if settings.verbose : print "Number of files in path with pattern '{}'".format(count,settings.syslogType)
    else:
        print Color.error + "\nThere are no file to analyze with pattern '{}'".format(settings.syslogType)
        print "List of files in path selected :\n"
        print settings.files
        print "\nTake care of file pattern to analyze. Use '-t' or '--type=' option to select file pattern (see help for more information)\n" + Color.nocolor
        exit()

def setPath():
    if settings.path =='':
        if not settings.workPathNeeded:
            settings.path = "/home/quentin/Python/Parser/results"
        else:
            import os
            user = os.getlogin()
            settings.path = "/var/fpwork/"+ str(user) + "/"+settings.branch+"/C_Test/SC_LTEL2/Sct/RobotTests/results"
    print "reference folder path for analysis : " + Color.bold + settings.path + Color.nocolor

def main(argv):
    import os
    os.system('clear')

    getArguments(argv)

    print Color.underline + "Starting {} tool\n".format(settings.application) + Color.nocolor

    printSelectedArguments()

    setPath()

    checkVersion()

    for dirpath, dirnames, filenames in os.walk(settings.path):
        if(dirnames!=[]):
            emTrace='activated'
            emTraceFolderName = dirnames[0]
        settings.files = [os.path.join(dirpath,name) for name in filenames]
        break
   
    checkFileNumber()
    checkFileType()

    settings.files.sort()

    if not isFolderAlreadyAnalyzed() : 
        fileHistory = open('fileHistory.txt','w')
        count = 0
        for filename in settings.files:
            if settings.syslogType in filename:
                count += 1
                fileHistory.write(filename+'\n')
        fileHistory.close()
        if settings.verbose : print "number of '{}' files in path: {}".format(settings.syslogType,count)

    
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

        os.makedirs(directory+'/throughput')
        os.makedirs(directory+'/cpuload')
        os.makedirs(directory+'/discard')

        # check board type and deployment from startup log
        getGlobalInformation()
        printGlobalInformation()

        pdcp = Pdcp()
        rlc  = Rlc()
        mac  = Mac()
        cpuload    = CpuLoad()
        commonStats = Common()

        print Color.bold + "\nread all files containing pattern '{}'".format(settings.syslogType) + Color.nocolor
        from datetime import datetime
        totalTime = datetime.now()
        for filename in settings.files:
            if settings.syslogType in filename:
                print "\n   read filename : " + filename
                Bar = ProgressBar(file_len(filename),60, ' ')
                d = datetime.now()
                with open(filename) as f:
                    lineNumber=0
                    for line in f:
                        lineNumber=lineNumber+1
                        if (lineNumber%2000==0):
                            Bar.update(lineNumber,datetime.now() - d)

                        cpuload.getCpuLoadStats(line)
                        pdcp.getStats(line)
                        rlc.getStats(line)
                        mac.getStats(line)

                        #PHY stub
                        # CBitrate:: ... Kilobits pers second on CellId.. 
                    Bar.update(lineNumber,datetime.now() - d)
                print ""
                Warning(filename)
                Error  (filename)
                Custom (filename)
        totalTime = datetime.now() - totalTime
        print "\n   \033[1mtotal time: {0:}:{1:02d}:{2:02d}.{3:03d}\033[0m\n".format(totalTime.seconds//3600,(totalTime.seconds//60)%60,totalTime.seconds,totalTime.microseconds/1000)


        commonStats.printStatistics()

        csvwriter = Csv()
        csvwriter.createCsvThroughput('downlink PDCP SDU',pdcp.dl.sdu.throughput)
        csvwriter.createCsvThroughput('downlink PDCP PDU',pdcp.dl.pdu.throughput)
        #csvwriter.createCsvThroughput('UL_PDCP',pdcp.getUlPdcpThroughput())
        #csvwriter.createCsvThroughput('DL_RLC',rlc.getDlRlcThroughput())
        csvwriter.createCsvThroughput('DL_RLC_SDU',rlc.sduThroughput)
        csvwriter.createCsvThroughput('DL_RLC_PDU',rlc.pduThroughput)
        #csvwriter.createCsvThroughput('UL_RLC',rlc.getUlRlcThroughput())
        #csvwriter.createCsvThroughput('DL_MAC',mac.getDlMacThroughput())
        #csvwriter.createCsvThroughput('DL_MAC_SDU',mac.sduThroughput)
        #csvwriter.createCsvThroughput('DL_MAC_PDU',mac.pduThroughput)
        #csvwriter.createCsvThroughput('UL_MAC',mac.getUlMacThroughput())

        #csvwriter.createCsv('DL_PDCP','discard',pdcp.getDlDiscard())

        #csvwriter.createCsvLoad(cpuload.getCpuLoad())
    else:
        print "\nResult folder already read and CSV for throughput and CPU load created."
        print "You can check files in csv folder where python script source file is present."

    if settings.graphAllowed or settings.plot:
        import graph
        print "\ndrawing graph mode has been set (-g or --show option). Plotting graph..."
        g = graph.Graph()
        if settings.console:
            g.drawConsole('PDCP')
        else:
            g.drawFigure()

    print "\n{} ended".format(settings.programName)

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
        if settings.verbose : print Color.warning + "no data collected for {} {}".format(name,type) + Color.nocolor
        return
    for core in data:
        directory = ''
        header= []
        if type=="throughput" :
            directory = 'throughput'
            header = ['timestamp','{} {} in kbps for core {}'.format(name,type,core)]
        elif type=="load" :
            directory = 'cpuload'
            header = ['timestamp','{} {} in % for core {}'.format(name,type,core)]
        elif type == 'discard' :
            directory = 'discard'
            header = ['timestamp','{} {} for core {}'.format(name,type,core)]
        else:
            print "csv file type not recognized"
            exit()

        if 'MAC' in name or 'UL_RLC' in name:
            # special case where uegroup in present in data...
            # this information is no everywhere in traces...
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
    if settings.verbose : print "CSV file created for {} {}".format(name,type)

def createCsvThroughput(layerName,data):
    createCsv(layerName,'throughput',data)

def createCsvLoad(data):
    createCsv('CPU','load',data)

if __name__ == "__main__":
    settings.init()
    import sys
    main(sys.argv[1:])  
