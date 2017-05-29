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
        self.map = {}
       
    def search(self, _string):
        m = self.regex.search(_string)
        return (m.group(1),m.group(2)) if m else ()

    def dump(self):
        print self.map
        

class CpuLoad(Parser):
    def __init__(self):
        Parser.__init__(self)
        self.type="syslog"
        self.regex = re.compile(r'(FSP-\d+|VM-\d+).*CPU_Load=(\d+\.?\d*)')

    def read(self):
        print "self.files: " + str(self.files)
        for filename in self.files:
            if(re.search(r'udplog_',filename)):
                print "read filename : " + filename
                with open(filename) as f:
                    for line in f:
                        values = Parser.search(self,line)
                        if(values!=()):
                            core=values[0]
                            load=values[1]
                            if core not in self.map:
                                self.map[core] = []
                            self.map[core].append(float(load))

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
    #path = "/home/quentin/Python/Parser/results"
    #user = os.environ['USER']
    user = os.getlogin()
    path = "/var/fpwork/"+ str(user) + "/FTL2/C_Test/SC_LTEL2/Sct/RobotTests/results"
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
    cpuload = CpuLoad()
    cpuload.read()
    cpuload.dump()

    #parse PDCP data
    #pdcp = PdcpPacket()
    #pdcp.read()
    #pdcp.dump()
    #print "received {} and sent {} PDPC packets".format(pdcp.noReceived(),pdcp.noSent())
    #print pdcp.averageReceived()

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
