#!/usr/bin/python2.7

class Parser:
    def __init__(self,_folder,_type):
        self.folder=_folder
        self.path= "/home/quentin/Python/"+ self.folder
        self.regex=''
        self.type=_type
        self.cpuload = 0

    def open(self):
        print "open folder " + self.folder
        import os
        for filename in os.listdir(self.path):
            print filename
            # if filename = *.log
            self.file = open(self.path+"/"+filename,"r")
            print self.file

    def match(self, expression, string):
        import re
        m = re.search(expression,string)
        if m:
            key   = m.group(1)
            value = m.group(2)
            return (key,value)
        else:
            return None

    def addToMap(self, pair):
        if(pair!=None):
            key = pair[0]
            value= pair[1]
            if key not in self.map:
                self.map[key] = []
            self.map[key].append(value)
        return self.map
        

class CpuLoad(Parser):
    def __init__(self):
        Parser.__init__(self,"results","syslog")
        self.cpuload = 0
        self.map = {}

    def read(self):
        Parser.open(self)
        print "read Cpu Load"
        import re
        for line in self.file:
            (core,load) = Parser.match(self,r'(FSP-\d+|\w+Vm) .* CPU [L|l]oad: (\d+)',line)
            self.map = Parser.addToMap(self,(core,load))

    def test(self):
        print self.map

    @property
    def cpuload(self):
        return self.cpuload

    @cpuload.setter
    def cpuload(self,v):
        self.cpuload = v


parser = CpuLoad()
parser.read()
parser.test()
print (parser.cpuload)
