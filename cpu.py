#!/usr/bin/python2.7

from parser import Parser
import re

class CpuLoad():
    def __init__(self):
        self.count = 0
        self.regex = None

    def read(self):
        self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.+)>.*CPU_Load=(\d+\.?\d*) max=(\d+\.?\d*)')
        self.count = 4

