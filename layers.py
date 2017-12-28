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

    @classmethod
    def printStatistics(cls):
        from settings import Color
        pipe = Color.bold + "|" + Color.nocolor 
        stats =  Color.bold + "   Other statistics:\n" \
        + "+----------------------------------------+----------------------------------------+\n" \
        + "|                MAC                     |                RLC                     |\n"\
        + "+----------------------------------------+----------------------------------------+\n"+ Color.nocolor\
        + pipe + "  total received TB      = {0:<11}  ".format(cls.receivedTBs)   \
        + pipe + "  total SRB SDUs         = {0:<11}  ".format(cls.srbSdus)       + pipe + '\n'\
        + pipe + "  total CRC failures     = {0:<11}  ".format(cls.crcFails)      \
        + pipe + "  total SRB SDU data     = {0:<11}  ".format(cls.srbSduData)    + pipe + '\n' \
        + pipe + "  total msg3s            = {0:<11}  ".format(cls.msg3s)         \
        + pipe + "  total UL NACK          = {0:<11}  ".format(cls.uplinkNack)    + pipe + '\n' \
        + pipe + "  total MAC CEs          = {0:<11}  ".format(cls.MacCEs)        \
        + pipe + "  total lost UM PDUs     = {0:<11}  ".format(cls.lostUmPdus)    + pipe + '\n' \
        + pipe + "  total paddingData      = {0:<11}  ".format(cls.paddingData)   \
        + pipe + "  total forwarded SDUs   = {0:<11}  ".format(cls.forwardedSdus) + pipe + '\n' \
        + pipe + "  total NOK Mac Headers  = {0:<11}  ".format(cls.nokMacHeader)  \
        + pipe + "  total AM PDU segments  = {0:<11}  ".format(cls.amPduSegments) + pipe + '\n' \
        + pipe + "  total RLC PDUs         = {0:<11}  ".format(cls.rlcPdus)       \
        + pipe + "  total NOK RLC Header   = {0:<11}  ".format(cls.nokRlcHeader)  + pipe + '\n' \
        + pipe + "  total DRB SDUs         = {0:<11}  ".format(cls.drbSdus)       \
        + pipe + "  total discarded PDU    = {0:<11}  ".format(cls.discardedPdu)  + pipe + '\n' \
        + Color.bold + '+----------------------------------------+----------------------------------------+\n' + Color.nocolor
        print stats

class PdcpStats:
    # DL
    dlbuffPkt = 0
    SDUTimerBasedDiscard = 0
    DLPDUAqmDiscard = 0
    DLPDUTimerBasedDiscard = 0
    DrbPdcpPduDiscardDueToStatusReport = 0
    DrbPdcpPduOutOfPdcpDescriptors = 0
    OutOfMemory = 0
    DLTotalDrbDiscard = 0
    DLTotalSrbDiscard = 0
    DLTotalGtpuDiscard = 0
    incomingPDCPSdu = 0
    DrbPdcpPduNacked = 0
    DrbPdcpPduAcked = 0

    # UL
    ulbuffPkt = 0
    PdcpPduStatusReport = 0
    PdcpPduRohcFeedback = 0

    @classmethod
    def printStatistics(cls):
        from settings import Color
        pipe = Color.bold + "|" + Color.nocolor 
        stats =  Color.bold + "   Other statistics:\n" \
        + "+---------------------------------------------------------------------------------+\n"\
        + "|                                    PDCP                                         |\n"\
        + "+---------------------------------------------------------------------------------+\n"+ Color.nocolor \
        + pipe + "  DL buffered packet                             = {0:<28}  ".format(cls.dlbuffPkt) + pipe + '\n'\
        + pipe + "  DL SDU Timer Based Discard                     = {0:<28}  ".format(cls.SDUTimerBasedDiscard)    + pipe + '\n'\
        + pipe + "  DL PDU Aqm discard                             = {0:<28}  ".format(cls.DLPDUAqmDiscard)        +pipe+ '\n'\
        + pipe + "  DL PDU Timer Based Discard                     = {0:<28}  ".format(cls.DLPDUTimerBasedDiscard)    + pipe + '\n'\
        + pipe + "  DL drb Pdcp Pdu Discard due to Status Report   = {0:<28}  ".format(cls.DrbPdcpPduDiscardDueToStatusReport) +pipe  + '\n'\
        + pipe + "  DL drb Pdcp Pdu Out Of Pdcp Descriptors        = {0:<28}  ".format(cls.DrbPdcpPduOutOfPdcpDescriptors)    + pipe  + '\n'\
        + pipe + "  DL Out Of Memory for Trsw Uplane Send Data msg:                                "   + pipe+ '\n' \
        + pipe + "     total drb discard                           = {0:<28}  ".format(cls.DLTotalDrbDiscard)    + pipe+ '\n'  \
        + pipe + "     total srb discard                           = {0:<28}  ".format(cls.DLTotalSrbDiscard)      +pipe+ '\n'  \
        + pipe + "     total gtpu discard                          = {0:<28}  ".format(cls.DLTotalGtpuDiscard)    + pipe + '\n' \
        + pipe + "  DL incoming PDCP Sdu                           = {0:<28}  ".format(cls.incomingPDCPSdu)     + pipe+ '\n'   \
        + pipe + "  DL Drb Pdcp pdu nacked max retrains exceeded   = {0:<28}  ".format(cls.DrbPdcpPduNacked)    + pipe+ '\n'  \
        + pipe + "  DL Drb Pdcp acked by Rlc                       = {0:<28}  ".format(cls.DrbPdcpPduAcked)  +pipe   + '\n'   \
        + Color.bold \
        + "+---------------------------------------------------------------------------------+\n"+ Color.nocolor \
        + pipe + "  UL buffered packet                             = {0:<28}  ".format(cls.ulbuffPkt) + pipe + '\n'\
        + pipe + "  UL pdcp pdu status report                      = {0:<28}  ".format(cls.PdcpPduStatusReport) + pipe + '\n'\
        + pipe + "  UL pdcp pdu feedback                           = {0:<28}  ".format(cls.PdcpPduRohcFeedback) + pipe + '\n'\
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


class Discard:
    pass

class OOM:
    pass

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

        self.stats.dl.discard = Discard()
        self.stats.dl.discard.SduT = r'PDCP/STATS/DISCARD/DL: SDU: T ([-]?\d+ [-]?\d+ [-]?\d+)'
        self.stats.dl.discard.PduA = r'PDCP/STATS/DISCARD/DL:.*PDU: A ([-]?\d+ [-]?\d+ [-]?\d+)'
        self.stats.dl.discard.PduT = r'PDCP/STATS/DISCARD/DL:.*PDU:.*T ([-]?\d+ [-]?\d+ [-]?\d+)'
        self.stats.dl.discard.SR   = r'PDCP/STATS/DISCARD/DL: SR: ([-]?\d+)'
        self.stats.dl.discard.OOD  = r'PDCP/STATS/DISCARD/DL:.*OOD: ([-]?\d+)'
        self.stats.dl.discard.oom  = OOM()
        self.stats.dl.discard.oom.drb  = r'PDCP/STATS/DISCARD/DL:.*OOM.*drb: ([-]?\d+)'
        self.stats.dl.discard.oom.srb  = r'PDCP/STATS/DISCARD/DL:.*OOM.*srb: ([-]?\d+)'
        self.stats.dl.discard.oom.gtpu = r'PDCP/STATS/DISCARD/DL:.*OOM.*gtpu: ([-]?\d+)'

        self.stats.dl.drbS1 = r'PDCP/STATS/DL: DRB S1: ([-]?\d+ [-]?\d+ [-]?\d+)'
        self.stats.dl.nack  = r'PDCP/STATS/DL:.*NACK: ([-]?\d+ [-]?\d+ [-]?\d+)'
        self.stats.dl.ack   = r'PDCP/STATS/DL:.*ACK: ([-]?\d+ [-]?\d+ [-]?\d+)'


        self.stats.ul.sr   = r'PDCP/STATS/UL:.*SR: ([-]?\d+)'
        self.stats.ul.rohc = r'PDCP/STATS/UL:.*RoHCF: ([-]?\d+)'

    def getDlStatistics(self,line):
        self.line = line
        self.get(self.stats.dl.buffPkt)
        if self.isValidData(): PdcpStats.dlbuffPkt += sum(self.value)

        self.get(self.stats.dl.discard.SduT)
        if self.isValidData(): PdcpStats.SDUTimerBasedDiscard += sum(self.value)
        self.get(self.stats.dl.discard.PduA)
        if self.isValidData(): PdcpStats.DLPDUAqmDiscard += sum(self.value)
        self.get(self.stats.dl.discard.PduT)
        if self.isValidData(): PdcpStats.DLPDUTimerBasedDiscard += sum(self.value)
        self.get(self.stats.dl.discard.SR)
        if self.isValidData(): PdcpStats.DrbPdcpPduDiscardDueToStatusReport += sum(self.value)
        self.get(self.stats.dl.discard.OOD)
        if self.isValidData(): PdcpStats.DrbPdcpPduOutOfPdcpDescriptors += sum(self.value)
        self.get(self.stats.dl.discard.oom.drb)
        if self.isValidData(): PdcpStats.DLTotalDrbDiscard += sum(self.value)
        self.get(self.stats.dl.discard.oom.srb)
        if self.isValidData(): PdcpStats.DLTotalSrbDiscard += sum(self.value)
        self.get(self.stats.dl.discard.oom.gtpu)
        if self.isValidData(): PdcpStats.DLTotalGtpuDiscard += sum(self.value)

        self.get(self.stats.dl.drbS1)
        if self.isValidData(): PdcpStats.incomingPDCPSdu += sum(self.value)
        self.get(self.stats.dl.nack)
        if self.isValidData(): PdcpStats.DrbPdcpPduNacked += sum(self.value)
        self.get(self.stats.dl.ack)
        if self.isValidData(): PdcpStats.DrbPdcpPduAcked += sum(self.value)


    def getUlStatistics(self,line):
        self.line = line
        self.get(self.stats.ul.buffPkt)
        if self.isValidData(): PdcpStats.ulbuffPkt += sum(self.value)

        self.get(self.stats.ul.sr)
        if self.isValidData(): PdcpStats.PdcpPduStatusReport += sum(self.value)
        self.get(self.stats.ul.rohc)
        if self.isValidData(): PdcpStats.PdcpPduRohcFeedback += sum(self.value)
        '''
        self.get(self.stats.ul.)
        if self.isValidData(): PdcpStats. += sum(self.value)
        self.get(self.stats.ul.)
        if self.isValidData(): PdcpStats. += sum(self.value)
        self.get(self.stats.ul.)
        if self.isValidData(): PdcpStats. += sum(self.value)
        self.get(self.stats.ul.)
        if self.isValidData(): PdcpStats. += sum(self.value)
        '''

    


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
        
class Gtp(Parser):
    ulrx = 0
    ultx = 0
    dlrx = 0
    dltx = 0
    issues = []
    def __init__(self):
        Parser.__init__(self)
        self.ul = Ul()
        self.dl = Dl()
        self.ul.sdu.field = r'DataGen/STATS.*Mbps.+=(\d+)'

        self.stats = Stats()
        self.stats.dl.rx = r'FSP-1264.*received currentSN=(\d+),'
        self.stats.dl.tx = r'VM-1170.*createGtpu\(size=\d+, seqNumber=(\d+)\)'
        self.stats.ul.rx = r'VM-1170.*received currentSN=(\d+)'
        self.stats.ul.expected = r'VM-1170.*expectedSN=(\d+)'
        self.stats.ul.tx = r'FSP-1264.*createGtpu\(size=\d+, seqNumber=(\d+)\)'

    def getStats(self,line):
        self.line = line
        self.get(self.stats.dl.rx)
        if self.isValidData(): self.dlrx += 1
        self.get(self.stats.dl.tx)
        if self.isValidData(): self.dltx += 1
        self.get(self.stats.ul.rx)
        if self.isValidData(): 
            self.ulrx += 1
            current = self.value[0]
        self.get(self.stats.ul.tx)
        if self.isValidData(): self.ultx += 1
        self.get(self.stats.ul.expected)
        if self.isValidData():
            if self.value[0] != current:
                self.issues.append(current)

    def printStatistics(self):
        print "DL packet sent : {1:<6} packet received: {0}".format(self.dlrx,self.dltx)
        print "UL packet sent : {1:<6} packet received: {0}".format(self.ulrx,self.ultx)
        if len(self.issues)!=0: 
            print "   SN issues : {}".format(self.issues)
        self.dlrx = 0
        self.dltx = 0
        self.ulrx = 0
        self.ultx = 0
        self.issues = []
