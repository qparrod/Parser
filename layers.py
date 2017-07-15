#!/usr/bin/python2.7

from parser import Parser
import re
import ptime

def fromByteToBit(val):
    return val * 8

class Common(Parser):
    srbSduData = 0
    receivedTBs = 0
    srbSdus = 0
    crcFails = 0
    msg3s = 0
    MacCEs = 0
    paddingData =0
    nokMacHeader = 0
    rlcPdus = 0
    drbSdus = 0
    lostUmPdus = 0
    discardedPdu = 0
    uplinkNack   = 0
    amPduSegments = 0
    nokRlcHeader = 0
    forwardedSdus = 0

    def __init__(self):
        Parser.__init__(self)

    def printStatistics(self):
        from settings import Color
        print Color.bold + '   Other statistics:' + Color.nocolor
        pipe = Color.bold + "|" + Color.nocolor 
        print Color.bold + '+------------------------------------+-----------------------------------+' + Color.nocolor
        print Color.bold + '|          MAC                       |              RLC                  |' + Color.nocolor
        print Color.bold + '+------------------------------------+-----------------------------------+' + Color.nocolor
        print pipe + " total received TB      = {0:<8}  ".format(Common.receivedTBs)  + pipe + "  total SRB SDUs        = {0:<8} ".format(Common.srbSdus)       + pipe
        print pipe + " total CRC failures     = {0:<8}  ".format(Common.crcFails)     + pipe + "  total SRB SDU data    = {0:<8} ".format(Common.srbSduData)    + pipe
        print pipe + " total msg3s            = {0:<8}  ".format(Common.msg3s)        + pipe + "  total UL NACK         = {0:<8} ".format(Common.uplinkNack)    + pipe
        print pipe + " total MAC CEs          = {0:<8}  ".format(Common.MacCEs)       + pipe + "  total lost UM PDUs    = {0:<8} ".format(Common.lostUmPdus)    + pipe
        print pipe + " total paddingData      = {0:<8}  ".format(Common.paddingData)  + pipe + "  total forwarded SDUs  = {0:<8} ".format(Common.forwardedSdus) + pipe
        print pipe + " total NOK Mac Headers  = {0:<8}  ".format(Common.nokMacHeader) + pipe + "  total AM PDU segments = {0:<8} ".format(Common.amPduSegments) + pipe
        print pipe + " total RLC PDUs         = {0:<8}  ".format(Common.rlcPdus)      + pipe + "  total NOK RLC Header  = {0:<8} ".format(Common.nokRlcHeader)  + pipe
        print pipe + " total DRB SDUs         = {0:<8}  ".format(Common.drbSdus)      + pipe + "  total discarded PDU   = {0:<8} ".format(Common.discardedPdu)  + pipe
        print Color.bold + '+------------------------------------+-----------------------------------+' + Color.nocolor

class PdcpPacket(Parser):
    def __init__(self):
        Parser.__init__(self)
        self.pdcpthroughput   = {}
        self.ulpdcpthroughput = {}
        #self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*PDCP/STATS/DISCARD/DL: SDU: T (\d+ \d+ \d+) PDU: A (\d+ \d+ \d+) T (\d+ \d+ \d+)')
        #self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*PDCP/STATS/DISCARD/DL: SR: (\d+) OOD: (\d+) OOM X2: (\d+) drb: (\d+) srb: (\d+) gtpu: (\d+)')
        #self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*PDCP/STATS/DL: SRB toRLC: (\d+ \d+ \d+) inBytes: (\d+ \d+ \d+) ACK: (\d+ \d+ \d+) NACK#1: (\d+ \d+ \d+) NACK#2: (\d+ \d+ \d+)')
        #self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*PDCP/STATS/DL: BuffPkt: (\d+ \d+ \d+) BuffData: (\d+ \d+ \d+) Fwd: (\d+ \d+ \d+) SA SwQ/Tx/Rx: \d+/\d+/\d+ \d+/\d+/\d+ \d+/\d+/\d+ \[\d+\] WinStall: (\d+ \d+ \d+)')
        #self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*PDCP/STATS/UL: DataPDU: (\d+ \d+ \d+) SR: (\d+) RoHCF: (\d+) toSGW: (\d+ \d+ \d+) Fwd: (\d+ \d+ \d+) BuffPkt: (\d+ \d+ \d+) BuffData: (\d+ \d+ \d+)')
        #self.count = 2

    def setDl(self):
        if (True): # cloud
            self.regex = re.compile(r'(VM-.+) (LINUX-Disp_\d) <(.*)>.*PDCP/STATS/DL: DRB S1: (\d+ \d+ \d+) X2: (\d+ \d+ \d+) inBytes: (\d+ \d+ \d+) toRLC: (\d+ \d+ \d+) inBytes: (\d+ \d+ \d+) ACK: (\d+ \d+ \d+) NACK: (\d+ \d+ \d+)')
            self.count = 10
        else:
            self.regex = re.compile(r'(FSP-\d+) <(.*)>.*PDCP/STATS/DL: DRB S1: (\d+ \d+ \d+) X2: (\d+ \d+ \d+) inBytes: (\d+ \d+ \d+) toRLC: (\d+ \d+ \d+) inBytes: (\d+ \d+ \d+) ACK: (\d+ \d+ \d+) NACK: (\d+ \d+ \d+)') 
            self.count = 9

    def setUl(self):
        self.regex = re.compile(r'(VM-.+) (LINUX-Disp_\d) <(.*)>.*PDCP/STATS/UL: DataPDU: (\d+ \d+ \d+)')
        self.count = 4

    def noReceived(self):
        return sum(element for element in self.map['receive']) if 'receive' in self.map.keys() else 0

    def noSent(self):
        return sum(element for element in self.map['send']) if 'send' in self.map.keys() else 0

    def averageReceived(self):
        return PdcpPacket.noReceived(self)/len(self.map['receive']) if len(self.map['receive'])!= 0 else 0

    def averageReceived(self):
        return PdcpPacket.noReceived(self)/len(self.map['send']) if len(self.map['send'])!= 0 else 0

    def getPdcpThroughputFromLine(self,pdcppacket,line):
        pdcppacket.setDl()
        values = self.search(line)
        if(values!=()):
            (soc, core,timestamp, s1, x2, inbytes, toRlc, inbytesRLC, ack, nack) = values
            values = [int(s) for s in inbytes.split() if s.isdigit()]
            if core not in self.pdcpthroughput:
                self.pdcpthroughput[core] = []
            t = ptime.Time(timestamp)
            timeDelta = 2.0 # 2 seconds between traces
            for i in reversed(range(len(values))):
                self.pdcpthroughput[core].append((t-timeDelta*i,fromByteToBit(values[len(values)-1-i])/timeDelta/1024))

        pdcppacket.setUl()
        values = self.search(line)
        if(values!=()):
            (soc,core,timestamp,data) = values
            values = [ int(s) for s in data.split() if s.isdigit() ]
            if core not in self.ulpdcpthroughput:
                self.ulpdcpthroughput[core] = []
            t = ptime.Time(timestamp)
            timeDelta = 2.0
            for i in reversed(range(len(values))):
                self.ulpdcpthroughput[core].append((t-timeDelta*i,fromByteToBit(values[len(values)-1-i])/timeDelta/1024))

    def getPDCPThroughput(self):
        return self.pdcpthroughput

    def getUlPdcpThroughput(self):
        return self.ulpdcpthroughput




class RlcPacket(Parser):
    def __init__(self):
        self.rlcthroughput  = {}
        self.ulrlcthroughput = {}

    def readRcvdRcvp(self):
        #self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*RLC/STATS/DL: RCVD: (\d+ \d+ \d+) RCVP: (\d+ \d+ \d+) ACKD: (\d+ \d+ \d+) ACKP: (\d+ \d+ \d+)')
        self.regex = re.compile(r'(FSP-\d+).*<(.*)>.*RLC/STATS/DL: RCVD: (\d+ \d+ \d+) RCVP: (\d+ \d+ \d+) ACKD: (\d+ \d+ \d+) ACKP: (\d+ \d+ \d+)') # filter VM
        self.count = 6

    def readUlRcvdRcvp(self):
        self.count = 0


    def readBuffer(self):
        self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*RLC/STATS/DL: BuffPkt: (\d+ \d+ \d+) BuffData: (\d+ \d+ \d+)')
        self.count = 4

    def readUlThroughputP1(self):
        self.regex = re.compile(r'(FSP-\d+).*<(.*)>.*ULUE STATS 1/.*x(\d)lF.*1:(\d+) 2:(\d+) 3:(\d+) 4:(\d+) 5:(\d+) 6:(\d+) 7:(\d+) 8:(\d+) 9:(\d+)')
        self.count = 12

    def getRlcThroughput(self,rlcpacket,line):
        self.readRcvdRcvp()
        values = self.search(line)
        if(values!=()):
            (core,timestamp,rcvd,rcvp,ackd,ackp)=values
            values = [int(s) for s in rcvd.split() if s.isdigit()]
            if core not in self.rlcthroughput:
                self.rlcthroughput[core] = []
            t = ptime.Time(timestamp)
            timeDelta = 2.0 # 2 seconds between traces
            for i in reversed(range(len(values))):
                self.rlcthroughput[core].append((t-timeDelta*i,fromByteToBit(values[len(values)-1-i])/timeDelta/1024))

        self.readUlThroughputP1()
        values = self.search(line)
        if(values!=()):
            (core,timestamp,ueGroup,recTBs,crcFails,msg3s,MacCEs,paddingData,NOK_MacHdrs,rlcPdus,rlcPduData,drbSdus)=values
            if core not in self.ulrlcthroughput:
                self.ulrlcthroughput[core] = []
            t = ptime.Time(timestamp)
            self.ulrlcthroughput[core].append((t-0,ueGroup,fromByteToBit(int(rlcPduData))/2.0/1024))
            Common.receivedTBs += int(recTBs)
            Common.crcFails += int(crcFails)
            Common.msg3s += int(msg3s)
            Common.MacCEs += int(MacCEs)
            Common.paddingData += int(paddingData)
            Common.nokMacHeader += int(NOK_MacHdrs)
            Common.rlcPdus += int(rlcPdus)
            Common.drbSdus += int(drbSdus)

    def getRLCThroughput(self):
        return self.rlcthroughput

    def getUlRlcThroughput(self):
        return self.ulrlcthroughput


class MacPacket(Parser):
    def __init__(self):
        self.count = 0
        self.macthroughput   = {}
        self.ulmacthroughput = {}

    def readReceivedData(self):
        self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*DLUE STATS 1/.*x(\d)lF.*/1:(\d+) 2:(\d+) 3:(\d+) 4:(\d+) 5:(\d+) 6:(\d+) 7:(\d+) 8:(\d+) 9:(\d+) 10:(\d+)')
        self.count = 13

    def readUlThroughputP2(self):
        self.regex = re.compile(r'(FSP-\d+).*<(.*)>.*ULUE STATS 2/.*x(\d)lF.*1:(\d+) 2:(\d+) 3:(\d+) 4:(\d+) 5:(\d+) 6:(\d+) 7:(\d+) 8:(\d+) 9:(\d+) ') # MAC
        self.count = 12
    
    def getMacThroughput(self,macpacket,line):
        self.readReceivedData()
        values = self.search(line)
        if(values!=()):
            (core,timestamp,ueGroup,receivedData,receivedPackets,ackedData,ackedPacket,nackedData,nackedPacket,amountOfBufferedSdus,amountOfBufferedData,amountOfWastedMemory,lostBsrCount)=values
            if core not in self.macthroughput:
                self.macthroughput[core] = []
            t = ptime.Time(timestamp)
            self.macthroughput[core].append((t-0,ueGroup,fromByteToBit(int(receivedData))/2.0/1024))

        self.readUlThroughputP2()
        values = self.search(line)
        if(values!=()):
            (core,timestamp,ueGroup,drbSduData,srbSdus,srbSduData,UlNack,lostUmPdus,forwardedSdus,AmPduSegments,NOK_RlcHdrs,discPdus)=values
            if core not in self.ulmacthroughput:
                self.ulmacthroughput[core] = []
            t = ptime.Time(timestamp)
            self.ulmacthroughput[core].append((t-0,ueGroup,fromByteToBit(int(drbSduData))/2.0/1024))
            Common.srbSduData    += int(srbSduData)
            Common.discardedPdu  += int(discPdus)
            Common.srbSdus       += int(srbSdus)
            Common.uplinkNack    += int(UlNack)
            Common.amPduSegments += int(AmPduSegments)
            Common.nokRlcHeader  += int(NOK_RlcHdrs)
            Common.forwardedSdus += int(forwardedSdus)
            Common.lostUmPdus    += int(lostUmPdus)

    def getMACThroughput(self):
        return self.macthroughput

    def getUlMacThroughput(self):
        return self.ulmacthroughput
        
