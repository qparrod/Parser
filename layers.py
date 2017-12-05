#!/usr/bin/python2.7

from parser import Parser
import re
import ptime

def fromByteToBit(val):
    return val * 8

class Common(Parser):
    srbSduData    = 0
    receivedTBs   = 0
    srbSdus       = 0
    crcFails      = 0
    msg3s         = 0
    MacCEs        = 0
    paddingData   = 0
    nokMacHeader  = 0
    rlcPdus       = 0
    drbSdus       = 0
    lostUmPdus    = 0
    discardedPdu  = 0
    uplinkNack    = 0
    amPduSegments = 0
    nokRlcHeader  = 0
    forwardedSdus = 0

    def __init__(self):
        Parser.__init__(self)

    def printStatistics(self):
        from settings import Color
        pipe = Color.bold + "|" + Color.nocolor 
        stats =  Color.bold + "   Other statistics:\n" \
        + "+----------------------------------------+----------------------------------------+\n" \
        + "|                MAC                     |                RLC                     |\n"\
        + "+----------------------------------------+----------------------------------------+\n"+ Color.nocolor\
        + pipe + "  total received TB      = {0:<11}  ".format(Common.receivedTBs)   \
        + pipe + "  total SRB SDUs         = {0:<11}  ".format(Common.srbSdus)       + pipe + '\n'\
        + pipe + "  total CRC failures     = {0:<11}  ".format(Common.crcFails)      \
        + pipe + "  total SRB SDU data     = {0:<11}  ".format(Common.srbSduData)    + pipe + '\n' \
        + pipe + "  total msg3s            = {0:<11}  ".format(Common.msg3s)         \
        + pipe + "  total UL NACK          = {0:<11}  ".format(Common.uplinkNack)    + pipe + '\n' \
        + pipe + "  total MAC CEs          = {0:<11}  ".format(Common.MacCEs)        \
        + pipe + "  total lost UM PDUs     = {0:<11}  ".format(Common.lostUmPdus)    + pipe + '\n' \
        + pipe + "  total paddingData      = {0:<11}  ".format(Common.paddingData)   \
        + pipe + "  total forwarded SDUs   = {0:<11}  ".format(Common.forwardedSdus) + pipe + '\n' \
        + pipe + "  total NOK Mac Headers  = {0:<11}  ".format(Common.nokMacHeader)  \
        + pipe + "  total AM PDU segments  = {0:<11}  ".format(Common.amPduSegments) + pipe + '\n' \
        + pipe + "  total RLC PDUs         = {0:<11}  ".format(Common.rlcPdus)       \
        + pipe + "  total NOK RLC Header   = {0:<11}  ".format(Common.nokRlcHeader)  + pipe + '\n' \
        + pipe + "  total DRB SDUs         = {0:<11}  ".format(Common.drbSdus)       \
        + pipe + "  total discarded PDU    = {0:<11}  ".format(Common.discardedPdu)  + pipe + '\n' \
        + Color.bold + '+----------------------------------------+----------------------------------------+\n' + Color.nocolor
        print stats

class PdcpPacket(Parser):
    def __init__(self):
        Parser.__init__(self)
        self.dlpdcpthroughput = {}
        self.ulpdcpthroughput = {}
        self.dldiscard = {}
        #self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*PDCP/STATS/DISCARD/DL: SDU: T (\d+ \d+ \d+) PDU: A (\d+ \d+ \d+) T (\d+ \d+ \d+)')
        #self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*PDCP/STATS/DISCARD/DL: SR: (\d+) OOD: (\d+) OOM X2: (\d+) drb: (\d+) srb: (\d+) gtpu: (\d+)')
        #self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*PDCP/STATS/DL: SRB toRLC: (\d+ \d+ \d+) inBytes: (\d+ \d+ \d+) ACK: (\d+ \d+ \d+) NACK#1: (\d+ \d+ \d+) NACK#2: (\d+ \d+ \d+)')
        #self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*PDCP/STATS/DL: BuffPkt: (\d+ \d+ \d+) BuffData: (\d+ \d+ \d+) Fwd: (\d+ \d+ \d+) SA SwQ/Tx/Rx: \d+/\d+/\d+ \d+/\d+/\d+ \d+/\d+/\d+ \[\d+\] WinStall: (\d+ \d+ \d+)')
        #self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*PDCP/STATS/UL: DataPDU: (\d+ \d+ \d+) SR: (\d+) RoHCF: (\d+) toSGW: (\d+ \d+ \d+) Fwd: (\d+ \d+ \d+) BuffPkt: (\d+ \d+ \d+) BuffData: (\d+ \d+ \d+)')

    def setDl(self):
        import settings
        self.data  = self.dlpdcpthroughput
        if settings.cloud:
            self.regex = re.compile(r'VM-.+ (LINUX-Disp_\d) <(.*)>.*PDCP/STATS/DL: DRB S1: (\d+ \d+ \d+) X2: (\d+ \d+ \d+) inBytes: (\d+ \d+ \d+) toRLC: (\d+ \d+ \d+) inBytes: (\d+ \d+ \d+) ACK: (\d+ \d+ \d+) NACK: (\d+ \d+ \d+)')
            self.count = 9
        else:
            self.regex = re.compile(r'FSP-\d+ <(.*)>.*PDCP/STATS/DL: DRB S1: (\d+ \d+ \d+) X2: (\d+ \d+ \d+) inBytes: (\d+ \d+ \d+) toRLC: (\d+ \d+ \d+) inBytes: (\d+ \d+ \d+) ACK: (\d+ \d+ \d+) NACK: (\d+ \d+ \d+)') 
            self.count = 8

    def setDiscardSdu(self):
        self.data  = self.dldiscard
        self.regex = re.compile(r'VM-.+ (LINUX-Disp_\d) <(.*)>.*PDCP/STATS/DISCARD/DL: SDU: T (\d+ \d+ \d+) PDU: A (\d+ \d+ \d+) T (\d+ \d+ \d+)')
        self.count = 4

    def setUl(self):
        self.data  = self.ulpdcpthroughput
        self.regex = re.compile(r'VM-.+ (LINUX-Disp_\d) <(.*)>.*PDCP/STATS/UL: DataPDU: (\d+ \d+ \d+) inBytes: (\d+ \d+ \d+)')
        self.count = 4

    def noReceived(self):
        return sum(element for element in self.map['receive']) if 'receive' in self.map.keys() else 0

    def noSent(self):
        return sum(element for element in self.map['send']) if 'send' in self.map.keys() else 0

    def averageReceived(self):
        return self.noReceived(self)/len(self.map['receive']) if len(self.map['receive'])!= 0 else 0

    def averageReceived(self):
        return self.noReceived(self)/len(self.map['send']) if len(self.map['send'])!= 0 else 0

    def getPdcpThroughputFromLine(self, line):
        self.line = line 

        self.setDl()
        self.get(4) #inbytes

        self.setUl()
        self.get(3) #DataPDU in bytes

        self.setDiscardSdu()
        self.get(2)


    def getDlPdcpThroughput(self):
        return self.dlpdcpthroughput

    def getUlPdcpThroughput(self):
        return self.ulpdcpthroughput

    def getDlDiscard(self):
        return self.dldiscard




class RlcPacket(Parser):
    def __init__(self):
        self.dlrlcthroughput  = {}
        self.ulrlcthroughput = {}

    def setDl(self):
        self.data  = self.dlrlcthroughput
        self.regex = re.compile(r'(FSP-\d+|VM-.*).*<(.*)>.*RLC/STATS/DL: RCVD: (\d+ \d+ \d+) RCVP: (\d+ \d+ \d+) ACKD: (\d+ \d+ \d+) ACKP: (\d+ \d+ \d+)')
        self.count = 6

    def readUlRcvdRcvp(self):
        self.count = 0

    #def readBuffer(self):
    #    self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*RLC/STATS/DL: BuffPkt: (\d+ \d+ \d+) BuffData: (\d+ \d+ \d+)')
    #    self.count = 4

    def setUl(self):
        self.regex = re.compile(r'(FSP-\d+).*<(.*)>.*ULUE STATS 1/.*x(\d)lF.*1:(\d+) 2:(\d+) 3:(\d+) 4:(\d+) 5:(\d+) 6:(\d+) 7:(\d+) 8:(\d+) 9:(\d+)')
        self.count = 12

    def getRlcThroughputFromLine(self,line):
        self.line = line
        self.setDl()
        self.get(2) # rcvd

        self.setUl()
        values = self.search(line)
        if(values!=()):
            (core,timestamp,ueGroup,recTBs,crcFails,msg3s,MacCEs,paddingData,NOK_MacHdrs,rlcPdus,rlcPduData,drbSdus)=values
            if core not in self.ulrlcthroughput:
                self.ulrlcthroughput[core] = []
            t = ptime.Time(timestamp)
            #self.ulrlcthroughput[core].append((t-0,ueGroup,fromByteToBit(int(rlcPduData))/2.0/1024))
            self.ulrlcthroughput[core].append((t-0,fromByteToBit(int(rlcPduData))/2.0/1024))
            Common.receivedTBs  += int(recTBs)
            Common.crcFails     += int(crcFails)
            Common.msg3s        += int(msg3s)
            Common.MacCEs       += int(MacCEs)
            Common.paddingData  += int(paddingData)
            Common.nokMacHeader += int(NOK_MacHdrs)
            Common.rlcPdus      += int(rlcPdus)
            Common.drbSdus      += int(drbSdus)

    def getDlRlcThroughput(self):
        return self.dlrlcthroughput

    def getUlRlcThroughput(self):
        return self.ulrlcthroughput


class MacPacket(Parser):
    def __init__(self):
        self.count = 0
        self.dlmacthroughput   = {}
        self.ulmacthroughput = {}

    def readReceivedData(self):
        self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*DLUE STATS 1/.*x(\d)lF.*/1:(\d+) 2:(\d+) 3:(\d+) 4:(\d+) 5:(\d+) 6:(\d+) 7:(\d+) 8:(\d+) 9:(\d+) 10:(\d+)')
        self.count = 13

    def readUlThroughputP2(self):
        self.regex = re.compile(r'(FSP-\d+).*<(.*)>.*ULUE STATS 2/.*x(\d).*1:(\d+) 2:(\d+) 3:(\d+) 4:(\d+) 5:(\d+) 6:(\d+) 7:(\d+) 8:(\d+) 9:(\d+)') # MAC
        self.count = 12
    
    def getMacThroughputFromLine(self,line):
        self.readReceivedData()
        values = self.search(line)
        if(values!=()):
            (core,timestamp,ueGroup,receivedData,receivedPackets,ackedData,ackedPacket,nackedData,nackedPacket,amountOfBufferedSdus,amountOfBufferedData,amountOfWastedMemory,lostBsrCount)=values
            if core not in self.dlmacthroughput:
                self.dlmacthroughput[core] = []
            t = ptime.Time(timestamp)
            #self.dlmacthroughput[core].append((t-0,ueGroup,fromByteToBit(int(receivedData))/2.0/1024))
            self.dlmacthroughput[core].append((t-0,fromByteToBit(int(receivedData))/2.0/1024))

        self.readUlThroughputP2()
        values = self.search(line)
        if values!=():
            (core,timestamp,ueGroup,drbSduData,srbSdus,srbSduData,UlNack,lostUmPdus,forwardedSdus,AmPduSegments,NOK_RlcHdrs,discPdus)=values
            if core not in self.ulmacthroughput:
                self.ulmacthroughput[core] = []
            t = ptime.Time(timestamp)
            #self.ulmacthroughput[core].append((t-0,ueGroup,fromByteToBit(int(drbSduData))/2.0/1024))
            self.ulmacthroughput[core].append((t-0,fromByteToBit(int(drbSduData))/2.0/1024))
            Common.srbSduData    += int(srbSduData)
            Common.discardedPdu  += int(discPdus)
            Common.srbSdus       += int(srbSdus)
            Common.uplinkNack    += int(UlNack)
            Common.amPduSegments += int(AmPduSegments)
            Common.nokRlcHeader  += int(NOK_RlcHdrs)
            Common.forwardedSdus += int(forwardedSdus)
            Common.lostUmPdus    += int(lostUmPdus)

    def getDlMacThroughput(self):
        return self.dlmacthroughput

    def getUlMacThroughput(self):
        return self.ulmacthroughput
        

class GtpPacket(Parser):
    def __init__(self):
        self.count=0
        self.ulgtpthroughput = {}

    def readUl(self):
        self.regex = re.compile(r'(FSP-\d+).*<(.*)>.*DataGen/STATS.*CPU_load=.*%.*Mbps.+=(\d+) pps=(\d+)') # GTPu from data generator
        self.count = 4

    def getGtpuThroughputFromLine(self,line):
        self.readUl()
        values = self.search(line)
        if values != ():
            (core,timestamp,mbps,pps) = values
            if core not in self.ulgtpthroughput:
                self.ulgtpthroughput[core] = []
            t = ptime.Time(timestamp)
            self.ulgtpthroughput[core].append((t-0,float(mbps)*1000))

    def getGtpuThroughput(self):
        return self.ulgtpthroughput