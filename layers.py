#!/usr/bin/python2.7

from parser import Parser
import re
import ptime

def fromByteToBit(val):
    return val * 8

class Common:
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

    #def __init__(self):
    #    Parser.__init__(self)

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

class PdcpStats:
    dlbuffPkt = 0
    ulbuffPkt = 0

    def printStatistics(self):
        from settings import Color
        pipe = Color.bold + "|" + Color.nocolor 
        stats =  Color.bold + "   Other statistics:\n" \
        + "+---------------------------------------------------------------------------------+\n"\
        + "|                                    PDCP                                         |\n"\
        + "+---------------------------------------------------------------------------------+\n"+ Color.nocolor \
        + pipe + "  DL buffered packet  = {0:<55}  ".format(PdcpStats.dlbuffPkt) + pipe + '\n'\
        + pipe + "  UL buffered packet  = {0:<55}  ".format(PdcpStats.ulbuffPkt) + pipe + '\n'\
        + Color.bold \
        + "+---------------------------------------------------------------------------------+\n"+ Color.nocolor
        print stats


class DlStats:
    pass

class UlStats:
    pass



class Stats:
    def __init__(self):
        self.dl = DlStats()
        self.ul = UlStats()

class Packet:
    def __init__(self):
        self.throughput     = {}
        self.numberOfPacket = {}
        self.discard        = {}
        self.field          = ''


class Sdu(Packet):
    def __init__(self):
        Packet.__init__(self)

class Pdu(Packet):
    def __init__(self):
        Packet.__init__(self)

class Dl:
    def __init__(self):
        self.sdu = Sdu()
        self.pdu = Pdu()

class Ul:
    def __init__(self):
        self.sdu = Sdu()
        self.pdu = Pdu()




class Pdcp(Parser):

    def __init__(self):
        Parser.__init__(self)
        self.dl = Dl()
        self.ul = Ul()

        self.dl.sdu.field = r'DRB.*X2:.*inBytes: (\d+ \d+ \d+) toRLC:'
        self.dl.pdu.field = r'DRB.*toRLC:.*inBytes: (\d+ \d+ \d+) ACK:'
        self.ul.sdu.field = r''
        self.ul.pdu.field = r'UL:.*inBytes: (\d+ \d+ \d+)' # Warning not available in product code. need a delivery before

        self.stats = Stats()
        self.stats.dl.buffPkt   = r'PDCP/STATS/DL: BuffPkt: ([-]?\d+ [-]?\d+ [-]?\d+)'
        self.stats.ul.buffPkt   = r'PDCP/STATS/UL:.*BuffPkt: ([-]?\d+ [-]?\d+ [-]?\d+)'

    def getDlStatistics(self,line):
        self.line = line
        self.get(self.stats.dl.buffPkt)
        if self.isValidData():
            PdcpStats.dlbuffPkt += self.value[0]

    def getUlStatistics(self,line):
        self.line = line
        self.get(self.stats.ul.buffPkt)
        if self.isValidData():
            PdcpStats.ulbuffPkt += self.value[0]
    


class Rlc(Parser):
    def __init__(self):
        Parser.__init__(self)
        self.dl = Dl()
        self.dl.sdu.field = r'RLC/STATS/DL: RCVD: (\d+ \d+ \d+)'
        self.dl.pdu.field = r'DLUE STATS 1.*8:(\d+)'

        self.ul = Ul()
        self.ul.sdu.field = r'ULUE STATS 2.*1:(\d+)'
        self.ul.pdu.field = r'ULUE STATS 1.*8:(\d+)'

        self.stats = Stats()
        self.stats.receivedTBs  = r'ULUE STATS 1/.*1:(\d+)'
        self.stats.crcFails     = r'ULUE STATS 1/.*2:(\d+)'
        self.stats.msg3s        = r'ULUE STATS 1/.*3:(\d+)'
        self.stats.MacCEs       = r'ULUE STATS 1/.*4:(\d+)'
        self.stats.paddingData  = r'ULUE STATS 1/.*5:(\d+)'
        self.stats.nokMacHeader = r'ULUE STATS 1/.*6:(\d+)'
        self.stats.rlcPdus      = r'ULUE STATS 1/.*7:(\d+)'
        self.stats.drbSdus      = r'ULUE STATS 1/.*8:(\d+)'

        self.stats.srbSdus       = r'ULUE STATS 2/.*2:(\d+)'
        self.stats.srbSduData    = r'ULUE STATS 2/.*3:(\d+)'
        self.stats.uplinkNack    = r'ULUE STATS 2/.*4:(\d+)'
        self.stats.lostUmPdus    = r'ULUE STATS 2/.*5:(\d+)'
        self.stats.forwardedSdus = r'ULUE STATS 2/.*6:(\d+)'
        self.stats.amPduSegments = r'ULUE STATS 2/.*7:(\d+)'
        self.stats.nokRlcHeader  = r'ULUE STATS 2/.*8:(\d+)'
        self.stats.discardedPdu  = r'ULUE STATS 2/.*9:(\d+)'

    def getDlSduStats(self,line):
        self.line = line
        self.get(self.stats.receivedTBs)
        if self.isValidData(): Common.receivedTBs += int(self.value[0])
        self.get(self.stats.crcFails)
        if self.isValidData(): Common.crcFails += int(self.value[0])
        self.get(self.stats.msg3s)
        if self.isValidData(): Common.msg3s += int(self.value[0])
        self.get(self.stats.MacCEs)
        if self.isValidData(): Common.MacCEs += int(self.value[0])
        self.get(self.stats.paddingData)
        if self.isValidData(): Common.paddingData += int(self.value[0])
        self.get(self.stats.nokMacHeader)
        if self.isValidData(): Common.nokMacHeader += int(self.value[0])
        self.get(self.stats.rlcPdus)
        if self.isValidData(): Common.rlcPdus += int(self.value[0])
        self.get(self.stats.drbSdus)
        if self.isValidData(): Common.drbSdus += int(self.value[0])

        self.get(self.stats.srbSduData)
        if self.isValidData(): Common.srbSduData += int(self.value[0])
        self.get(self.stats.discardedPdu)
        if self.isValidData(): Common.discardedPdu += int(self.value[0])
        self.get(self.stats.srbSdus)
        if self.isValidData(): Common.srbSdus += int(self.value[0])
        self.get(self.stats.uplinkNack)
        if self.isValidData(): Common.uplinkNack += int(self.value[0])
        self.get(self.stats.amPduSegments)
        if self.isValidData(): Common.amPduSegments += int(self.value[0])
        self.get(self.stats.nokRlcHeader)
        if self.isValidData(): Common.nokRlcHeader += int(self.value[0])
        self.get(self.stats.forwardedSdus)
        if self.isValidData(): Common.forwardedSdus += int(self.value[0])
        self.get(self.stats.lostUmPdus)
        if self.isValidData(): Common.lostUmPdus += int(self.value[0])


class Mac(Parser):
    def __init__(self):
        Parser.__init__(self)
        self.dl = Dl()
        self.dl.sdu.field = r'DLUE STATS 1/.*8:(\d+)'
        self.dl.pdu.field = r''

        self.ul = Ul()
        self.ul.sdu.field = r'ULUE STATS 1/.*1:(\d+)'
        self.ul.pdu.field = r''
        
'''
class Gtp(Parser):
    def __init__(self):
        Parser.__init__(self)
        self.ul = Ul()
        self.dl = Dl()
        #self.count=0
        #self.ulgtpthroughput = {}
        self.ul.sdu.field = r'DataGen/STATS.*Mbps.+=(\d+)'


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
'''