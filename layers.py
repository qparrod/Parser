#!/usr/bin/python2.7

from parser import Parser
import re
import ptime

def fromByteToBit(val):
    return val * 8

class PdcpPacket(Parser):
    def __init__(self):
        self.regex = None
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
        values = self.search(pdcppacket,line)
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
        values = self.search(pdcppacket,line)
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




class RlcPacket(Parser):
    def __init__(self):
        self.count = 0
        self.rlcthroughput  = {}
        self.ulrlcthroughput = {}
!
    def readRcvdRcvp(self):
        #self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*RLC/STATS/DL: RCVD: (\d+ \d+ \d+) RCVP: (\d+ \d+ \d+) ACKD: (\d+ \d+ \d+) ACKP: (\d+ \d+ \d+)')
        self.regex = re.compile(r'(FSP-\d+).*<(.*)>.*RLC/STATS/DL: RCVD: (\d+ \d+ \d+) RCVP: (\d+ \d+ \d+) ACKD: (\d+ \d+ \d+) ACKP: (\d+ \d+ \d+)') # filter VM
        self.count = 6

    def readUlRcvdRcvp(self):
        self.count = 0


    def readBuffer(self):
        self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*RLC/STATS/DL: BuffPkt: (\d+ \d+ \d+) BuffData: (\d+ \d+ \d+)')
        self.count = 4

    def getRlcThroughput(self,rlcpacket,line):
        rlcpacket.readRcvdRcvp()
        values = self.search(rlcpacket,line)
        if(values!=()):
            (core,timestamp,rcvd,rcvp,ackd,ackp)=values
            values = [int(s) for s in rcvd.split() if s.isdigit()]
            if core not in self.rlcthroughput:
                self.rlcthroughput[core] = []
            t = ptime.Time(timestamp)
            timeDelta = 2.0 # 2 seconds between traces
            for i in reversed(range(len(values))):
                self.rlcthroughput[core].append((t-timeDelta*i,fromByteToBit(values[len(values)-1-i])/timeDelta/1024))


class MacPacket(Parser):
    def __init__(self):
        self.count = 0
        self.macthroughput   = {}
        self.ulmacthroughput = {}

    def readReceivedData(self):
        self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*DLUE STATS 1/.*x(\d)lF.*/1:(\d+) 2:(\d+) 3:(\d+) 4:(\d+) 5:(\d+) 6:(\d+) 7:(\d+) 8:(\d+) 9:(\d+) 10:(\d+)')
        self.count = 13

    def readUlThroughputP1(self):
        self.regex = re.compile(r'(FSP-\d+).*<(.*)>.*ULUE STATS 1/.*x(\d)lF.*1:(\d+) 2:(\d+) 3:(\d+) 4:(\d+) 5:(\d+) 6:(\d+) 7:(\d+) 8:(\d+) 9:(\d+)') # MAC
        self.count = 12

    def readUlThroughputP2(self):
        self.regex = re.compile(r'(FSP-\d+).*<(.*)>.*ULUE STATS 2/.*x(\d)lF.*1:(\d+) 2:(\d+) 3:(\d+) 4:(\d+) 5:(\d+) 6:(\d+) 7:(\d+) 8:(\d+) 9:(\d+) ') # MAC
        self.count = 12
    
    def getMacThroughput(self,macpacket,line):
        macpacket.readReceivedData()
        values = self.search(macpacket,line)
        if(values!=()):
            (core,timestamp,ueGroup,receivedData,receivedPackets,ackedData,ackedPacket,nackedData,nackedPacket,amountOfBufferedSdus,amountOfBufferedData,amountOfWastedMemory,lostBsrCount)=values
            if core not in self.macthroughput:
                self.macthroughput[core] = []
            t = ptime.Time(timestamp)
            self.macthroughput[core].append((t-0,ueGroup,fromByteToBit(int(receivedData))/2.0/1024))

        macpacket.readUlThroughputP1()
        values = self.search(macpacket,line)
        if(values!=()):
            (core,timestamp,ueGroup,recTBs,crcFails,msg3s,MacCEs,paddingData,NOK_MacHdrs,rlcPdus,rlcPduData,drbSdus)=values
            if core not in self.ulrlcthroughput:
                self.ulrlcthroughput[core] = []
            t = ptime.Time(timestamp)
            self.ulrlcthroughput[core].append((t-0,ueGroup,fromByteToBit(int(rlcPduData))/2.0/1024))
            self.receivedTBs += int(recTBs)
            self.crcFails += int(crcFails)
            self.msg3s += int(msg3s)
            self.MacCEs += int(MacCEs)
            self.paddingData += int(paddingData)
            self.nokMacHeader += int(NOK_MacHdrs)
            self.rlcPdus += int(rlcPdus)
            self.drbSdus += int(drbSdus)

        macpacket.readUlThroughputP2()
        values = self.search(macpacket,line)
        if(values!=()):
            (core,timestamp,ueGroup,drbSduData,srbSdus,srbSduData,UlNack,lostUmPdus,forwardedSdus,AmPduSegments,NOK_RlcHdrs,discPdus)=values
            if core not in self.ulmacthroughput:
                self.ulmacthroughput[core] = []
            t = ptime.Time(timestamp)
            self.ulmacthroughput[core].append((t-0,ueGroup,fromByteToBit(int(drbSduData))/2.0/1024))
            self.srbSduData    += int(srbSduData)
            self.discardedPdu  += int(discPdus)
            self.srbSdus       += int(srbSdus)
            self.uplinkNack    += int(UlNack)
            self.amPduSegments += int(AmPduSegments)
            self.nokRlcHeader  += int(NOK_RlcHdrs)
            self.forwardedSdus += int(forwardedSdus)
            self.lostUmPdus    += int(lostUmPdus)
        
