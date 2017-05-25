#!/usr/bin/python2.7

import re

class Parser:
    def __init__(self):
        self.regex=''
        self.type=""
        self.files = files
        self.regex = None
        self.map = {}
        

    def search(self, _string):
        m = self.regex.search(_string)
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

    def dump(self):
        print self.map
        

class CpuLoad(Parser):
    def __init__(self):
        Parser.__init__(self)
        self.type="syslog"
        self.regex = re.compile(r'(FSP-\d+|\w+Vm) .* CPU [Ll]oad: (\d+)')

    def read(self):
        for filename in self.files:
            with open(filename) as f:
                for line in f:
                    Parser.addToMap(self,Parser.search(self,line)) # pair is (core,load)


class PdcpPacket(Parser):
    def __init__(self):
        Parser.__init__(self)
        self.type = "syslog"
        self.toto = 0

import os
path  = "/home/quentin/Python/Parser/results"
files = [path+"/"+filename for filename in os.listdir(path)]
print files

cpuload = CpuLoad()
cpuload.read()
cpuload.dump()

pdcp = PdcpPacket()
pdcp.dump()