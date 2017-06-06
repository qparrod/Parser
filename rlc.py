#!/usr/bin/python2.7

from parser import Parser

class RlcPacket(Parser):
    def __init__(self):
        self.count = 0

    def readRcvdRcvp(self):
        self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*RLC/STATS/DL: RCVD: (\d+ \d+ \d+) RCVP: (\d+ \d+ \d+) ACKD: (\d+ \d+ \d+) ACKP: (\d+ \d+ \d+)')
        self.count = 6


    def readBuffer(self):
        self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*RLC/STATS/DL: BuffPkt: (\d+ \d+ \d+) BuffData: (\d+ \d+ \d+)')
        self.count = 4