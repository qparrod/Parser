#!/usr/bin/python2.7

from parser import Parser
import re

class PdcpPacket(Parser):
    def __init__(self):
        self.regex = None
        Parser.__init__(self)
        #self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*PDCP/STATS/DISCARD/DL: SDU: T (\d+ \d+ \d+) PDU: A (\d+ \d+ \d+) T (\d+ \d+ \d+)')
        #self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*PDCP/STATS/DISCARD/DL: SR: (\d+) OOD: (\d+) OOM X2: (\d+) drb: (\d+) srb: (\d+) gtpu: (\d+)')
        #self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*PDCP/STATS/DL: SRB toRLC: (\d+ \d+ \d+) inBytes: (\d+ \d+ \d+) ACK: (\d+ \d+ \d+) NACK#1: (\d+ \d+ \d+) NACK#2: (\d+ \d+ \d+)')
        #self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*PDCP/STATS/DL: BuffPkt: (\d+ \d+ \d+) BuffData: (\d+ \d+ \d+) Fwd: (\d+ \d+ \d+) SA SwQ/Tx/Rx: \d+/\d+/\d+ \d+/\d+/\d+ \d+/\d+/\d+ \[\d+\] WinStall: (\d+ \d+ \d+)')
        #self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*PDCP/STATS/UL: DataPDU: (\d+ \d+ \d+) SR: (\d+) RoHCF: (\d+) toSGW: (\d+ \d+ \d+) Fwd: (\d+ \d+ \d+) BuffPkt: (\d+ \d+ \d+) BuffData: (\d+ \d+ \d+)')
        #self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*DLUE STATS \d/.*1:(\d+) 2:(\d+) 3:(\d+) 4:(\d+) 5:(\d+) 6:(\d+) 7:(\d+)') # MAC
        #self.regex = re.compile(r'8:(\d+) 9:(\d+) 10:(\d+)')
        #self.count = 2

    def setDl(self):
        if (True): # cloud
            self.regex = re.compile(r'(VM-\d+) (LINUX-Disp_\d) <(.*)>.*PDCP/STATS/DL: DRB S1: (\d+ \d+ \d+) X2: (\d+ \d+ \d+) inBytes: (\d+ \d+ \d+) toRLC: (\d+ \d+ \d+) inBytes: (\d+ \d+ \d+) ACK: (\d+ \d+ \d+) NACK: (\d+ \d+ \d+)')
            self.count = 10
        else:
            self.regex = re.compile(r'(FSP-\d+) <(.*)>.*PDCP/STATS/DL: DRB S1: (\d+ \d+ \d+) X2: (\d+ \d+ \d+) inBytes: (\d+ \d+ \d+) toRLC: (\d+ \d+ \d+) inBytes: (\d+ \d+ \d+) ACK: (\d+ \d+ \d+) NACK: (\d+ \d+ \d+)') 
            self.count = 9

    def setUl(self):
        self.regex = re.compile(r'(VM-\d+) (LINUX-Disp_\d) <(.*)>.*PDCP/STATS/UL: DataPDU: (\d+ \d+ \d+)')
        self.count = 4

    def noReceived(self):
        return sum(element for element in self.map['receive']) if 'receive' in self.map.keys() else 0

    def noSent(self):
        return sum(element for element in self.map['send']) if 'send' in self.map.keys() else 0

    def averageReceived(self):
        return PdcpPacket.noReceived(self)/len(self.map['receive']) if len(self.map['receive'])!= 0 else 0

    def averageReceived(self):
        return PdcpPacket.noReceived(self)/len(self.map['send']) if len(self.map['send'])!= 0 else 0




class RlcPacket(Parser):
    def __init__(self):
        self.count = 0

    def readRcvdRcvp(self):
        #self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*RLC/STATS/DL: RCVD: (\d+ \d+ \d+) RCVP: (\d+ \d+ \d+) ACKD: (\d+ \d+ \d+) ACKP: (\d+ \d+ \d+)')
        self.regex = re.compile(r'(FSP-\d+).*<(.*)>.*RLC/STATS/DL: RCVD: (\d+ \d+ \d+) RCVP: (\d+ \d+ \d+) ACKD: (\d+ \d+ \d+) ACKP: (\d+ \d+ \d+)') # filter VM
        self.count = 6




    def readBuffer(self):
        self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*RLC/STATS/DL: BuffPkt: (\d+ \d+ \d+) BuffData: (\d+ \d+ \d+)')
        self.count = 4


class MacPacket(Parser):
    def __init__(self):
        self.count =0

    def readReceivedData(self):
        self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*DLUE STATS 1/.*x(\d)lF.*/1:(\d+) 2:(\d+) 3:(\d+) 4:(\d+) 5:(\d+) 6:(\d+) 7:(\d+) 8:(\d+) 9:(\d+) 10:(\d+)')
        self.count = 13
