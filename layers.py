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
        + "+-------------------------------------+-------------------------------------+\n" \
        + "|              MAC                    |              RLC                    |\n"\
        + "+-------------------------------------+-------------------------------------+\n"+ Color.nocolor\
        + pipe + "  total received TB      = {0:<8}  ".format(Common.receivedTBs)   \
        + pipe + "  total SRB SDUs         = {0:<8}  ".format(Common.srbSdus)       + pipe + '\n'\
        + pipe + "  total CRC failures     = {0:<8}  ".format(Common.crcFails)      \
        + pipe + "  total SRB SDU data     = {0:<8}  ".format(Common.srbSduData)    + pipe + '\n' \
        + pipe + "  total msg3s            = {0:<8}  ".format(Common.msg3s)         \
        + pipe + "  total UL NACK          = {0:<8}  ".format(Common.uplinkNack)    + pipe + '\n' \
        + pipe + "  total MAC CEs          = {0:<8}  ".format(Common.MacCEs)        \
        + pipe + "  total lost UM PDUs     = {0:<8}  ".format(Common.lostUmPdus)    + pipe + '\n' \
        + pipe + "  total paddingData      = {0:<8}  ".format(Common.paddingData)   \
        + pipe + "  total forwarded SDUs   = {0:<8}  ".format(Common.forwardedSdus) + pipe + '\n' \
        + pipe + "  total NOK Mac Headers  = {0:<8}  ".format(Common.nokMacHeader)  \
        + pipe + "  total AM PDU segments  = {0:<8}  ".format(Common.amPduSegments) + pipe + '\n' \
        + pipe + "  total RLC PDUs         = {0:<8}  ".format(Common.rlcPdus)       \
        + pipe + "  total NOK RLC Header   = {0:<8}  ".format(Common.nokRlcHeader)  + pipe + '\n' \
        + pipe + "  total DRB SDUs         = {0:<8}  ".format(Common.drbSdus)       \
        + pipe + "  total discarded PDU    = {0:<8}  ".format(Common.discardedPdu)  + pipe + '\n' \
        + Color.bold + '+-------------------------------------+-------------------------------------+\n' + Color.nocolor
        print stats

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
        self.ul.pdu.field = r'UL: DataPDU: (\d+ \d+ \d+)' # probably packets and not bytes

        #self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*PDCP/STATS/DISCARD/DL: SDU: T (\d+ \d+ \d+) PDU: A (\d+ \d+ \d+) T (\d+ \d+ \d+)')
        #self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*PDCP/STATS/DISCARD/DL: SR: (\d+) OOD: (\d+) OOM X2: (\d+) drb: (\d+) srb: (\d+) gtpu: (\d+)')
        #self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*PDCP/STATS/DL: SRB toRLC: (\d+ \d+ \d+) inBytes: (\d+ \d+ \d+) ACK: (\d+ \d+ \d+) NACK#1: (\d+ \d+ \d+) NACK#2: (\d+ \d+ \d+)')
        #self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*PDCP/STATS/DL: BuffPkt: (\d+ \d+ \d+) BuffData: (\d+ \d+ \d+) Fwd: (\d+ \d+ \d+) SA SwQ/Tx/Rx: \d+/\d+/\d+ \d+/\d+/\d+ \d+/\d+/\d+ \[\d+\] WinStall: (\d+ \d+ \d+)')
        #self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*PDCP/STATS/UL: DataPDU: (\d+ \d+ \d+) SR: (\d+) RoHCF: (\d+) toSGW: (\d+ \d+ \d+) Fwd: (\d+ \d+ \d+) BuffPkt: (\d+ \d+ \d+) BuffData: (\d+ \d+ \d+)')



class Rlc(Parser):
    def __init__(self):
        Parser.__init__(self)
        self.dl = Dl()
        self.ul = Ul()

        self.dl.sdu.field = r'RLC/STATS/DL: RCVD: (\d+ \d+ \d+)'
        self.dl.pdu.field = r'DLUE STATS 1.*8: (\d+ \d+ \d+)'
        self.ul.sdu.field = r'ULUE STATS 2.*1: (\d+ \d+ \d+)'
        self.ul.pdu.field = r'ULUE STATS 1.*8: (\d+ \d+ \d+)'


    '''
    def setUl(self):
        self.regex = re.compile(r'(FSP-\d+).*<(.*)>.*ULUE STATS 1/.*x(\d)lF.*1:(\d+) 2:(\d+) 3:(\d+) 4:(\d+) 5:(\d+) 6:(\d+) 7:(\d+) 8:(\d+) 9:(\d+)')

    def getRlcThroughputFromLine(self,line):
        self.line = line
        self.setDl()
        self.get(2) # rcvd

        self.setUl()
        values = self.search()
        if(values!=()):
            (core,timestamp,ueGroup,recTBs,crcFails,msg3s,MacCEs,paddingData,NOK_MacHdrs,rlcPdus,rlcPduData,drbSdus)=values
            if core not in self.ulrlcthroughput:
                self.ulrlcthroughput[core] = []
            t = ptime.Time(timestamp)
            self.ulrlcthroughput[core].append((t-0,ueGroup,fromByteToBit(int(rlcPduData))/2.0/1024))
            Common.receivedTBs  += int(recTBs)
            Common.crcFails     += int(crcFails)
            Common.msg3s        += int(msg3s)
            Common.MacCEs       += int(MacCEs)
            Common.paddingData  += int(paddingData)
            Common.nokMacHeader += int(NOK_MacHdrs)
            Common.rlcPdus      += int(rlcPdus)
            Common.drbSdus      += int(drbSdus)
    '''


class Mac(Parser):
    def __init__(self):
        Parser.__init__(self)
        self.dl = Dl()
        self.ul = Ul()

        self.dl.sdu.field = r'DLUE STATS 1.*x(\d)l.*8: (\d+ \d+ \d+)'
        self.dl.pdu.field = r'DLUE STATS 1.*x(\d)l.*8: (\d+ \d+ \d+)'
        self.ul.sdu.field = r'ULUE STATS 1.*x(\d)l.*1: (\d+ \d+ \d+)'
        self.ul.pdu.field = r''

        self.hasUeGroup      = True


    '''
    def readReceivedData(self):
        self.regex = re.compile(r'(FSP-\d+|VM-\d+).*<(.*)>.*DLUE STATS 1/.*x(\d)lF.*/1:(\d+) 2:(\d+) 3:(\d+) 4:(\d+) 5:(\d+) 6:(\d+) 7:(\d+) 8:(\d+) 9:(\d+) 10:(\d+)')

    def readUlThroughputP2(self):
        self.regex = re.compile(r'(FSP-\d+).*<(.*)>.*ULUE STATS 2/.*x(\d)lF.*1:(\d+) 2:(\d+) 3:(\d+) 4:(\d+) 5:(\d+) 6:(\d+) 7:(\d+) 8:(\d+) 9:(\d+) ') # MAC
    
    def getMacThroughputFromLine(self,line):
        self.readReceivedData()
        self.line = line
        values = self.search()
        if(values!=()):
            (core,timestamp,ueGroup,receivedData,receivedPackets,ackedData,ackedPacket,nackedData,nackedPacket,amountOfBufferedSdus,amountOfBufferedData,amountOfWastedMemory,lostBsrCount)=values
            if core not in self.dlmacthroughput:
                self.dlmacthroughput[core] = []
            t = ptime.Time(timestamp)
            self.dlmacthroughput[core].append((t-0,ueGroup,fromByteToBit(int(receivedData))/2.0/1024))

        self.readUlThroughputP2()
        values = self.search()
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
    '''
        
