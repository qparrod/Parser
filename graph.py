#!/usr/bin/python2.7

import ptime
import settings
from settings import *

class Graph:
    def __init__(self):
        self.data = {}
        self.layer = ''

    def exit(self):
        import curses
        curses.nocbreak()
        self.screen.keypad(0)
        curses.echo()
        curses.endwin()
        #exit()


    def drawBoxes(self):
        v_box = 10
        h_box = h_max
        scr_boxes = []
        v_box_origin = 0
        h_box_origin = 0
        box_space = 0

        while(v_box_origin+v_box<v_max):
            scr = curses.newwin(v_box,h_box,v_box_origin,h_box_origin)
            scr.border('|','|','_','_','|','|','|','|')
            scr_boxes.append(scr)
            v_box_origin += v_box + box_space -1
         
        for scr in scr_boxes:
            scr.refresh()
        scr_boxes[-1].getch()

    def getDataFromFile(self,filePath):
        import csv
        with open(filePath,'r') as csvfile:
            r = csv.reader(csvfile, delimiter=',') 
            
            if self.core not in self.data:
                self.data[self.core] = {}
            for row  in r:
                if len(row) != 2:
                    print "wrong csv format for {}".format(self.layer)
                    exit()
                # retrieve header
                if row[0] == 'timestamp':
                    continue

                if self.ueGroup not in self.data[self.core]:
                    self.data[self.core][self.ueGroup] = []

                self.data[self.core][self.ueGroup].append(row)

    def getData(self,layer):
        self.layer = layer
        self.cores = self.getCoreName()
        self.data  = {}
        for core in self.cores:
            self.core = core
            self.ueGroup = 0 if 'MAC' not in self.layer else core[-1]
            csvFilePath = 'csv/throughput/{}_throughput_{}.csv'.format(self.layer,core)
            self.getDataFromFile(csvFilePath)

    def getCoreName(self):
        from os import listdir
        from os.path import isfile, join
        path = 'csv/throughput'
        files = [f for f in listdir(path) if (isfile(join(path, f)) and self.layer in f)]

        import re
        cores = []
        for f in files:
            m = re.search(r'.+_throughput_(.+).csv',f)
            if (m):
                cores.append(m.group(1))
        return cores

    def draw(self,layer):
        if settings.verbose : print "   graph: draw {}".format(layer)
        self.getData(layer)

        import matplotlib.dates as dt
        import matplotlib.pyplot as plt
        refLength = 0
        refCore   = ''
        for core in self.data:
            for ueGroup in self.data[core]:
                if (refLength ==0 ):
                    refLength = len(self.data[core][ueGroup])
                    refCore   = core
                if (refLength!=0 and refLength!=len(self.data[core][ueGroup])):
                    print Color.warning + "   Warning on {}: values of core {} have not same size then {}: {} != {}".format(layer, core, refCore, refLength, len(self.data[core][ueGroup])) + Color.nocolor
                    break
        
        sumordinate = [0] * refLength
        dates = []
        for core in self.data:
            for ueGroup in self.data[core]:
                absciss = [ ptime.Time(format='%Y-%m-%d %H:%M:%S.%f').convertTimestampFromStringToTime(data[0]) for data in self.data[core][ueGroup] ]
                ordinate = [float(data[1]) for data in self.data[core][ueGroup]] # value to plot
                sumordinate = [e1 + e2 for e1,e2 in zip(sumordinate,ordinate)]

                t = [ ptime.Time(format='%H:%M:%S').convertLocalTime(i) for i in absciss ]
                dates = dt.date2num(t)

                plt.plot_date(dates,ordinate,'-', label='{} throughput in kbps'.format(core))
                plt.title('{} throughput'.format(self.layer))
                plt.xticks( rotation=25 )

        plt.plot_date(dates[:refLength], sumordinate, '--',label='total throughput in kbps', linewidth=4)
        plt.legend()
        #plt.legend(bbox_to_anchor=(1.05, 1), loc=2, shadow=True, borderaxespad=0.)


    def drawFigure(self):
        import matplotlib.pyplot as plt
        import settings

        mydpi = settings.dpi 
        if settings.verbose : print "   DPI (dots per inch) for images set to {}.".format(mydpi)
        print "   Creating figure. This can take few seconds..."
        fig = plt.figure(1,figsize=(800/mydpi,800/mydpi),dpi=mydpi)
        print "   figure created"
        plt.subplot(3,2,1); self.draw('DL_PDCP')
        plt.subplot(3,2,2); self.draw('UL_PDCP')
        plt.subplot(3,2,3); self.draw('DL_RLC')
        plt.subplot(3,2,4); self.draw('UL_RLC')
        plt.subplot(3,2,5); self.draw('DL_MAC')
        plt.subplot(3,2,6); self.draw('UL_MAC')
        
        if settings.png  : fig.savefig('throughput.png', dpi=100)
        if settings.plot : plt.show()


    def printAxes(self):
        self.screen.addstr(self.Y(self.v_size+1),self.X(0),'^')
        self.screen.vline(self.Y(self.v_size-1),self.X(0),'|',self.v_size)
        self.screen.addstr(self.Y(0),self.X(0),'|')
        self.screen.hline(self.Y(0),self.X(1),'_',self.h_size)
        self.screen.addstr(self.Y(0),self.X(self.h_size),'>')

    def printLegend(self,xlegend,ylegend):
        self.screen.addstr(self.Y(-2),self.X(0.5*(self.h_size-len(xlegend))),xlegend)
        self.screen.addstr(self.Y(self.v_size),self.X(2),ylegend)

    def X(self,x):
        X = int(self.x_origin + x)
        (Ymax,Xmax) = self.screen.getmaxyx()
        if X > Xmax or X < 0:
            raise RuntimeError("invalid conversion from x={} to X={} -> max={}".format(x,X,Xmax))
            self.exit()
        return X

    def Y(self,y):
        Y = int(self.y_origin + self.v_size - y)
        (Ymax,Xmax) = self.screen.getmaxyx()
        if Y > Ymax or Y < 0:
            self.exit()
            raise RuntimeError("invalid conversion from y={} to Y={} -> max={}".format(y,Y,Ymax))
        return Y

    def convertCoord(self,x,y):
        return (self.X(x),self.Y(y))

    def convertCoordList(self,list_x, list_y):
        coord_list = zip(list_x,list_y)
        return [(self.X(x),self.Y(y)) for x,y in coord_list]

    def printXRange(self,min,max):
        mintime = ptime.Time(format='%H:%M:%S').convertLocalTimeToTime(min)#time.strftime('%H:%M:%S',time.localtime(min))
        self.screen.addstr(self.Y(-1),self.X(0),mintime)

        maxtime = ptime.Time(format='%H:%M:%S').convertLocalTimeToTime(max) #time.strftime('%H:%M:%S',time.localtime(max))
        self.screen.addstr(self.Y(-1),self.X(self.h_size-len(maxtime)),maxtime)

    def printYRange(self,min,max):
        self.screen.addstr(self.Y(self.v_size),self.X(-1-len(str(int(max)))), str(int(max)))
        self.screen.addstr(self.Y(0)          ,self.X(-1-len(str(int(min)))), str(int(min)))

    def consoleInit(self):
        self.x_origin = 10
        self.y_origin = 2
        self.x_limit = 4
        self.y_limit = 5
        (v_max,h_max) = self.screen.getmaxyx()
        self.h_size = h_max-self.x_limit-self.x_origin-1
        self.v_size = v_max-self.y_limit-self.y_origin-1

    def getMaxLength(self):
        l = 0
        for core in self.data:
            if (l ==0 ):
                l = len(self.data[core])
            if (l!=0 and l!=len(self.data[core])):
                print "values have not same size: {} != {}".format(l,len(self.data[core]))
                self.exit()
        return l

    def drawConsole(self,layer):
        import curses

        self.screen = curses.initscr()
        curses.start_color()
        self.consoleInit()

        (v_max,h_max) = self.screen.getmaxyx()

        self.screen.clear()
        self.screen.border('|','|','-','-','+','+','+','+')
        
        self.screen.addstr(self.Y(v_max-6),self.X(20),"{} throughput ({},{}) ".format(layer,v_max,h_max))

        self.printAxes()
        self.printLegend('time','throughput in kbps')

        color = [curses.COLOR_RED,curses.COLOR_GREEN,curses.COLOR_BLUE,curses.COLOR_CYAN,curses.COLOR_MAGENTA,curses.COLOR_YELLOW]
        curses.init_pair(1, color[1], curses.COLOR_BLACK)
        curses.init_pair(2, color[2], curses.COLOR_BLACK)
        curses.init_pair(3, color[3], curses.COLOR_BLACK)
        curses.init_pair(4, color[4], curses.COLOR_BLACK)
        curses.init_pair(5, color[5], curses.COLOR_BLACK)
        
        self.getData(layer)

        l = self.getMaxLength()
        sumordinate = [0] * l

        # Calculate time to print in console
        import sys
        hmax = 0
        hmin = sys.maxint
        vmax=0
        vmin= sys.maxint
        for core in self.data:
            absciss = [ ptime.Time(format='%Y-%m-%d %H:%M:%S.%f').convertFromStringToLocalTime(pair[0]) for pair in self.data[core] ]
            ordinate = [float(pair[1]) for pair in self.data[core]] # values to plot
            sumordinate = [e1 + e2 for e1,e2 in zip(sumordinate,ordinate)]
            hmin = min(hmin,min(absciss))
            hmax = max(hmax,max(absciss))
            vmin = min(vmin,min(ordinate))
            vmax = max(vmax,max(sumordinate))
        hstep = float((hmax-hmin)/self.h_size)
        vstep = float((vmax-vmin)/self.v_size)

        # print ranges
        self.printYRange(vmin,vmax)
        self.printXRange(hmin,hmax)


        colorIdx = 0
        for core in self.data:
            colorIdx += 1
            absciss = [ ptime.Time(format='%Y-%m-%d %H:%M:%S.%f').convertFromStringToLocalTime(pair[0]) for pair in self.data[core] ]
            ordinate = [float(pair[1]) for pair in self.data[core]] # value to plot

            coord = zip(absciss,ordinate)
            for x,y in coord:
                xpos = int((x-min(absciss))/hstep)
                ypos = int((y-min(ordinate))/vstep)
                self.screen.addstr(self.Y(ypos),self.X(xpos),'+',curses.color_pair(colorIdx))
                
        # print sum
        colorIdx += 1
        tmp = (0,0)
        sum = zip(absciss,sumordinate)
        for x,y in sum:
            xpos = int((x - min(absciss)) / hstep)
            ypos = int((y - min(sumordinate)) / vstep )
            
            self.screen.addstr(self.Y(ypos),self.X(xpos),'*',curses.color_pair(colorIdx))
            tmp = (xpos,ypos)

        self.screen.refresh()
        self.screen.getch()

        self.exit()
