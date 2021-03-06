#!/usr/bin/python2.7

import re
from layers import *
#from pool import PoolStats
import settings
from settings import Color,ProgressBar
from csvWriter import *
from filter import *

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1



class Check:

    color = Color.nocolor

    def __init__(self,path):
        self.count     = 0
        self.extension = '.txt'
        self.checkFile(path)
        self.printResult()

    def checkFile(self, path):
        fd = open(self.type + self.extension,'a')
        with open(path,'r') as f:
            fd.write("---- in file {} :\n".format(path))
            for line in f:
                for pattern in self.patterns:
                    if re.search(r'{}'.format(pattern),line):
                        toFilter = False
                        for e in Filter.error:
                            if e in line:
                               toFilter = True
                               break
                        for w in Filter.warning:
                            if w in line:
                               toFilter = True
                               break
                        if not toFilter:
                            self.count += 1
                            fd.write(line)
        fd.close()

    def printResult(self):
        if self.count != 0:
            print self.color + "       Number of {0:<7} : {1:}".format(self.type,self.count) + Color.nocolor

class Warning(Check):
    def __init__(self,path):
        self.type     = 'warning'
        self.patterns = ['WRN','Warning','WARNING']
        self.color = Color.warning
        Check.__init__(self,path)
        

class Error(Check):
    def __init__(self,path):
        self.type     = 'error'
        self.patterns = ['ERR','error','ERROR']
        self.color = Color.error
        Check.__init__(self,path)

class Custom(Check):
    def __init__(self,path):
        self.type     = "custom"
        self.patterns = ['long event detected']
        Check.__init__(self,path)






class Parser:

    timeDelta = 2.0

    def __init__(self):
        self.regex    = ''
        self.files    = settings.files
        self.regex    = None
        self.line     = ''
        self.core      = None
        self.timestamp = None
        self.data      = None

    def fromByteToBit(self,val):
        return val * 8

    def convertToKbps(self,val):
        return val / 1024

    def get(self, pos, dump=False):
        import ptime

        values = self.search(self.line)
        if values != () :
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
                self.data[core].append( (timeInDatetime, throughputInkbps))
            if dump: 
                print "".format(core)
                print values

    def fill(self, obj):
        if self.value:
            if self.core not in obj:
                obj[self.core] = []
            for i in range(len(self.timestamp)):
                obj[self.core].append( (self.timestamp[i], self.value[i]) )

    def getValue(self,string):
        regex = re.compile(string)
        m = re.search(regex,self.line)
        return m.group(1) if m else None

    def get(self,regex):
        if regex == r'': return
        self.data      = self.getValue(regex)
        if not self.data : return 
        self.core      = self.getValue(r'^.*(LINUX-Disp_\d|FSP-\d+) ')
        self.timestamp = self.getValue(r'^.*<(.*Z)> ')

        if not self.core or not self.timestamp or not self.data : return
        self.value     = [ int(s) for s in self.data.split() ] if self.data else []
        if self.data == []: return
        if self.timestamp :
            import ptime
            t = ptime.Time(self.timestamp)

            self.timestamp = []
            for i in reversed(range(len(self.value))): # len != 0 when there are 3 data for every 2 seconds
                self.timestamp.append( t - i * Parser.timeDelta )

    def calculateThroughput(self):
        self.value = [ int(v) * 8 / 1024  / 2.0  for v in self.value ] # in kbps

    def isValidData(self):
        if not self.core or not self.timestamp or not self.data : return False
        return True

    def getDlSduThroughput(self):
        self.get(self.dl.sdu.field)
        if not self.isValidData() : return
        self.calculateThroughput()
        self.fill( self.dl.sdu.throughput )

    def getDlPduThroughput(self):
        self.get(self.dl.pdu.field)
        if not self.isValidData() : return
        self.calculateThroughput()
        self.fill( self.dl.pdu.throughput )

    def getUlSduThroughput(self):
        self.get(self.ul.sdu.field)
        if not self.isValidData() : return
        self.calculateThroughput()
        self.fill( self.ul.sdu.throughput )

    def getUlPduThroughput(self):
        self.get(self.ul.pdu.field)
        if not self.isValidData() : return
        self.calculateThroughput()
        self.fill( self.ul.pdu.throughput )

    def getDlStats(self):
        self.getDlSduThroughput()
        self.getDlPduThroughput()

    def getUlStats(self):
        self.getUlSduThroughput()
        self.getUlPduThroughput()

    def getStats(self,line):
        self.line = line
        self.getDlStats()
        self.getUlStats()



class CpuLoad(Parser):
    '''
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
    '''

    def __init__(self):
        Parser.__init__(self)
        self.stats = r'DLUE STATS 1/.*8:(\d+)'




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
    if (settings.cloud): 
        settings.deployment = 'cBTS ' + settings.deployment 

def printGlobalInformation():
    print '\033[1m'+'+'+'-'*60+'+'
    print "|{0:<18}{1:>2} {2:<20}{3:>20}".format("application type",":",settings.application,"|")
    print "|{0:<18}{1:>2} {2:<20}{3:>20}".format("board type",":",settings.board,"|")
    print "|{0:<18}{1:>2} {2:<20}{3:>20}".format("deployment",":",settings.deployment,"|")
    print '+'+'-'*60+'+' + Color.nocolor

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
    print "   -f|--file          select a specific file to analyze. Example: -f /var/fpwork/user/test.txt"
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
        opts, args = getopt.getopt(argv,"hi:a:b:gw:cmp:vt:f:",["application=","board=","wcpy=","png","dpi=","show","clear","type","path","cloud","file"])
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
            settings.workPathNeeded = True
            settings.branch         = arg
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
        elif opt in ('-f', "--file"):
            settings.file         = arg
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
        if settings.path !='' : print "    path '{}' selected (-p)".format(settings.path)
        if settings.graphAllowed and settings.console : print "    graph will be displayed on console (-c)"
        if settings.file !='' : print "    file {} is selected (-f)".format(settings.file)


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

def createHistoryFile():
    fileHistory = open('fileHistory.txt','w')
    count = 0
    for filename in settings.files:
        if settings.syslogType in filename:
            count += 1
            fileHistory.write(filename+'\n')
    fileHistory.close()
    return count

def checkFileCount(count):
    if settings.verbose : print "number of '{}' files in path: {}".format(settings.syslogType,count)
    if count == 0:
        print Color.error + "\nNo file found. Exiting now." 
        print "Take care on -f, -p or -w options" + Color.nocolor
        exit()

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
   
    if settings.file == '': 
        checkFileNumber()
        checkFileType()
        settings.files.sort()
    else:
        settings.files.append(settings.file)

    # check board type and deployment from startup log
    getGlobalInformation()
    printGlobalInformation()

    if not isFolderAlreadyAnalyzed() :
        count = createHistoryFile()
        checkFileCount(count)
    
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

        pdcp = Pdcp()
        rlc  = Rlc()
        mac  = Mac()
        gtp  = Gtp()

        cpuload     = CpuLoad()

        print Color.bold + "\nread all files containing pattern '{}'".format(settings.syslogType) + Color.nocolor
        from datetime import datetime
        totalTime = datetime.now()
        for filename in settings.files:
            if settings.syslogType in filename:
                print "\n   read filename : " + filename
                Bar = ProgressBar(file_len(filename),60, ' ')
                d = datetime.now()

                filter=False
                for f in settings.fileFilter:
                    if f in filename:
                        filter = True
                        break

                if not filter:
                    with open(filename) as f:
                        lineNumber=0
                        for line in f:
                            lineNumber=lineNumber+1
                            if (lineNumber%2000==0):
                                Bar.update(lineNumber,datetime.now() - d)

                            pdcp.getStats(line)
                            rlc.getStats(line)
                            mac.getStats(line)
                            gtp.getStats(line)


                            pdcp.getDlStatistics(line)
                            pdcp.getUlStatistics(line)
                            rlc.getDlSduStats(line)

                            #cpuload.getStats(line)

                        Bar.update(lineNumber,datetime.now() - d)
                    print ""

                Warning(filename)
                Error  (filename)
                Custom (filename)
                gtp.printStatistics()
        totalTime = datetime.now() - totalTime
        print "\n   \033[1mtotal time: {0:}:{1:02d}:{2:02d}.{3:03d}\033[0m\n".format(totalTime.seconds//3600,(totalTime.seconds//60)%60,totalTime.seconds,totalTime.microseconds/1000)

        PdcpStats.printStatistics()
        Common.printStatistics()

        csvwriter = Csv()
        csvwriter.createCsvThroughput('downlink PDCP SDU',pdcp.dl.sdu.throughput)
        csvwriter.createCsvThroughput('downlink PDCP PDU',pdcp.dl.pdu.throughput)
        csvwriter.createCsvThroughput('downlink RLC SDU',rlc.dl.sdu.throughput)
        csvwriter.createCsvThroughput('downlink RLC PDU',rlc.dl.pdu.throughput)
        csvwriter.createCsvThroughput('downlink MAC SDU',mac.dl.sdu.throughput)
        csvwriter.createCsvThroughput('downlink MAC PDU',mac.dl.pdu.throughput)
        csvwriter.createCsvThroughput('uplink PDCP SDU',pdcp.ul.sdu.throughput)
        csvwriter.createCsvThroughput('uplink PDCP PDU',pdcp.ul.pdu.throughput)
        csvwriter.createCsvThroughput('uplink RLC SDU',rlc.ul.sdu.throughput)
        csvwriter.createCsvThroughput('uplink RLC PDU',rlc.ul.pdu.throughput)
        csvwriter.createCsvThroughput('uplink MAC SDU',mac.ul.sdu.throughput)
        csvwriter.createCsvThroughput('uplink MAC PDU',mac.ul.pdu.throughput)


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

if __name__ == "__main__":
    settings.init()
    import sys
    main(sys.argv[1:])  
