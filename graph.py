#!/usr/bin/python2.7

import ptime
import settings
from settings import *

class Graph:
    def __init__(self):
        self.data = {}
        self.layer = ''

    def getDataFromFile(self,filePath):
        import csv

        try:
            with open(filePath,'r') as csvfile:
                r = csv.reader(csvfile, delimiter=',') 
                
                if self.core not in self.data:
                    self.data[self.core] = []
                for row  in r:
                    if len(row) != 2:
                        print "wrong csv format for {}".format(self.layer)
                        exit()
                    # retrieve header
                    if row[0] == 'timestamp':
                        continue
                    self.data[self.core].append(row)
        except IOError as e:
            print Color.error+ "I/O error({}): {}: {}".format(e.errno, e.strerror,filePath) + Color.nocolor

    def getThroughputData(self,layer):
        self.layer = layer
        self.cores = self.getCoreName('throughput')
        self.data  = {}
        for core in self.cores:
            self.core    = core # may have ueGroup in it
            csvFilePath  = 'csv/throughput/{}_throughput_{}.csv'.format(self.layer,self.core)
            self.getDataFromFile(csvFilePath)

    def getDiscardData(self,layer):
        self.layer = layer
        self.cores = self.getCoreName('discard')
        self.data  = {}
        for core in self.cores:
            self.core    = core
            csvFilePath  = 'csv/discard/{}_discard_{}.csv'.format(self.layer,core)
            self.getDataFromFile(csvFilePath)

    def getCoreName(self,folder):
        from os import listdir
        from os.path import isfile, join
        path = 'csv/{}'.format(folder)
        files = [f for f in listdir(path) if (isfile(join(path, f)) and self.layer in f)]

        import re
        cores = []
        for f in files:
            m = re.search(r'.+_throughput_(.+).csv',f)
            if (m):
                cores.append(m.group(1))
        return cores

    def draw(self):
        print "   graph: draw discard"

    def getDirection(self,layer):
        direction = None
        if 'downlink' in layer: direction = 'DL'
        elif 'uplink' in layer: direction = 'UL'
        else:
            print "throughput direction not recognized in layer ({})".format(layer)
            exit()
        return direction
        

    def drawTitles(self):
        import matplotlib.pyplot as plt
        if 'downlink' or 'DL' or 'dl' in self.layer:
            if 'PDCP' in self.layer:
                plt.title('DL PDCP PDU throughput (kbps)')
            elif 'RLC' in self.layer:
                plt.title('DL RLC throughput (kbps)')
            elif 'MAC' in self.layer:
                plt.title('DL MAC throughput (kbps)')
        elif 'uplink' or 'UL' or 'ul' in self.layer:
            if 'PDCP' in self.layer:
                plt.title('UL PDCP PDU throughput (kbps)')
            elif 'RLC' in self.layer:
                plt.title('UL RLC PDU throughput (kbps)')
            elif 'MAC' in self.layer:
                plt.title('UL MAC throughput (kbps)')

    def getValuesToDraw(self,layer):
        if settings.verbose : print "\n\n   graph: getValuesToDraw for {}".format(layer)
        self.getThroughputData(layer)

        import matplotlib.dates as dt

        sumordinate = []
        refabs      = []
        result = {}

        # SUT
        sut_cores = settings.SUTCores[settings.deployment][self.getDirection(layer)]
        for core in self.data:
            if core not in sut_cores:
                if settings.verbose: print "core {} filtered {} {} -> {}".format(core,settings.deployment,layer,self.getDirection(layer))
                continue

            absciss = [ ptime.Time(format='%Y-%m-%d %H:%M:%S.%f').convertTimestampFromStringToTime(data[0]) for data in self.data[core] ]
            ordinate = [float(data[1]) for data in self.data[core] ]

            t = [ ptime.Time(format='%H:%M:%S').convertLocalTime(i) for i in absciss ] 

            roundtime     = [ ptime.Time().round(i,roundTo=1) for i in t ]
            roundordinate = ordinate[:] # copy all the list

            # filter tuples by aggregating values
            todel = []
            for i in range(len(roundtime)):
                if i+1 < len(roundtime) and roundtime[i]==roundtime[i+1]:
                    roundordinate[i+1] += roundordinate[i]
                    todel.append(i)
            for i in reversed(todel):
                del roundtime[i]
                del roundordinate[i]

            # create sum of plots
            if len(sumordinate) == 0:
                refabs = roundtime[:]
                sumordinate = [0] * len(refabs)

            todel = []
            for i in reversed(range(len(refabs))):
                if refabs[i] not in roundtime:
                    todel.append(i)
                else:
                    sumordinate[i] += roundordinate[roundtime.index(refabs[i])]

            for idx in todel:
                del sumordinate[idx]
                del refabs[idx]

            if core not in result:
                result[core] = zip(dt.date2num(t),ordinate)

            total = zip(dt.date2num(refabs), sumordinate)
        return result, total



    def draw(self,values, total):
        import matplotlib.dates as dt
        import matplotlib.pyplot as plt

        for core in values:
            x = [ value[0] for value in values[core] ]
            y = [ value[1] for value in values[core] ]

            plt.gca().xaxis.set_major_formatter(dt.DateFormatter('%H:%M:%S'))
            plt.plot(x, y, label=core)
            plt.ylabel('throughput in kbps')
            plt.xticks( rotation=25 )
            self.drawTitles()

        x = [ v[0] for v in total ]
        y = [ v[1] for v in total ]
        plt.plot(x, y, '--',color='red',label='total', linewidth=4)
        plt.legend(loc='upper right',shadow=True, fancybox=True)



    def drawFigure(self):
        import matplotlib.pyplot as plt
        import settings

        dlpdcpsduvalues, total_dlpdcpsduvalues = self.getValuesToDraw('downlink PDCP SDU')
        ulpdcpsduvalues, total_ulpdcpsduvalues = self.getValuesToDraw('uplink PDCP SDU')
        dlrlcsduvalues, total_dlrlcsduvalues   = self.getValuesToDraw('downlink RLC SDU')
        ulrlcsduvalues, total_ulrlcsduvalues   = self.getValuesToDraw('uplink RLC SDU')
        dlmacsduvalues, total_dlmacsduvalues   = self.getValuesToDraw('downlink MAC SDU')
        ulmacsduvalues, total_ulmacsduvalues   = self.getValuesToDraw('uplink MAC SDU')

        if settings.plot : 
            mydpi = settings.dpi 
            if settings.verbose : print "   DPI (dots per inch) for images set to {}.".format(mydpi)
            print "   Creating figure. This can take few seconds..."
            fig = plt.figure(1,figsize=(800/mydpi,1000/mydpi),dpi=mydpi)
            print "   figure created"
            plt.suptitle('throughput in SUT',fontsize=16)
            plt.subplot(3,2,1); self.draw(dlpdcpsduvalues, total_dlpdcpsduvalues)
            plt.subplot(3,2,2); self.draw(ulpdcpsduvalues, total_ulpdcpsduvalues)
            plt.subplot(3,2,3); self.draw(dlrlcsduvalues, total_dlrlcsduvalues)
            plt.subplot(3,2,4); self.draw(ulrlcsduvalues, total_ulrlcsduvalues)
            plt.subplot(3,2,5); self.draw(dlmacsduvalues, total_dlmacsduvalues)
            plt.subplot(3,2,6); self.draw(ulmacsduvalues, total_ulmacsduvalues)

            plt.show()


        #fig2 = plt.figure(2)
        #self.draw('DL_PDCP')
        
        if settings.png  : fig.savefig('throughput.png', dpi=100)