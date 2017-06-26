#!/usr/bin/python2.7

import time
import datetime

def convertTimestampFromStringToTime(timestampInString):
    import datetime
    pattern = "%Y-%m-%d %H:%M:%S.%f"
    dt = datetime.datetime.strptime(timestampInString, pattern) # create a datetime
    st = dt.timetuple() # create a time.struct_time
    return time.mktime(st) # create a 9-tuple expressed time in local time


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
        exit()


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

    def getData(self):
        import csv
        self.data = {}
        for core in self.cores:
            with open('csv/throughput/{}_throughput_{}.csv'.format(self.layer,core),'r') as csvfile:
                r = csv.reader(csvfile, delimiter=',') 
                self.data[core] = []
                for row  in r:
                    if len(row) != 2:
                        print "wrong csv format"
                        exit()
                    # retrieve header
                    if row[0] == 'timestamp':
                        continue
                    pair = (row[0],row[1])
                    self.data[core].append(pair)

    def getPdcpData(self):
        # TODO find core on available csv file
        pdcpcore = ['LINUX-Disp_0','LINUX-Disp_1']
        self.cores = pdcpcore
        self.layer = 'PDCP'
        self.getData()


    def getRlcData(self):
        # TODO: find core on reading csv file available
        rlccore = ['FSP-1231','FSP-1232','FSP-1233','FSP-1234']
        self.cores = rlccore
        self.layer = 'RLC'
        self.getData()

    def getMacData(self):
        # TODO: find core on reading csv file available
        maccore = ['FSP-1233','FSP-1253']
        self.cores = maccore
        self.layer = 'MAC'
        self.getData()
        

    def drawPdcp(self):
        self.getPdcpData()
        self.layer = 'PDCP'
        self.draw()

    def drawRlc(self):
        self.getRlcData()
        self.layer = 'RLC'
        self.draw()

    def drawMac(self):
        self.getMacData()
        self.layer = 'MAC'
        self.draw()

    def draw(self):
        import matplotlib.dates as dt
        import matplotlib.pyplot as plt
        l = 0
        for core in self.data:
            if (l ==0 ):
                l = len(self.data[core])
            if (l!=0 and l!=len(self.data[core])):
                print "values have not same size: {} != {}".format(l,len(self.data[core]))
                break #exit()
        sumordinate = [0] * l
        for core in self.data:
            absciss = [ convertTimestampFromStringToTime(pair[0]) for pair in self.data[core] ]
            ordinate = [float(pair[1]) for pair in self.data[core]] # value to plot
            sumordinate = [e1 + e2 for e1,e2 in zip(sumordinate,ordinate)]

            t = [datetime.datetime.strptime(time.strftime('%H:%M:%S',time.localtime(int(i))),'%H:%M:%S') for i in absciss]
            dates = dt.date2num(t)

            plt.plot_date(dates,ordinate,'-', label='{} throughput in kbps'.format(core))
            plt.title('{} throughput'.format(self.layer))
            #plt.xticks( rotation=25 )

        plt.plot_date(dates[:l],sumordinate, '--',label='total throughput in kbps')
        plt.legend(bbox_to_anchor=(1.1, 1.05), shadow=True)


    def drawFigure(self):
        import matplotlib.pyplot as plt

        mydpi = 50

        fig = plt.figure(1,figsize=(800/mydpi,800/mydpi),dpi=mydpi)

        #fig = plt.figure(1)

        plt.subplot(3,1,1)
        self.drawPdcp()

        plt.subplot(3,1,2)
        self.drawRlc()
        
        plt.subplot(3,1,3)
        self.drawMac()

        fig.savefig('throughput.png', dpi=100)

        plt.show()


    def printAxes(self):
        self.screen.addstr(self.Y(self.v_size+1),self.X(0),'^')
        self.screen.vline(self.Y(self.v_size-1),self.X(0),'|',self.v_size)
        self.screen.addstr(self.Y(0),self.X(0),'|')
        self.screen.hline(self.Y(0),self.X(1),'_',self.h_size)
        self.screen.addstr(self.Y(0),self.X(self.h_size),'>')

    def printLegend(self,xlegend,ylegend):
        self.screen.addstr(self.Y(-2),self.X(0.5*(self.h_size-len(xlegend))),xlegend)
        self.screen.addstr(self.Y(self.v_size,self.X(2)),ylegend)

    def X(self,x):
        X = int(self.x_origin + x)
        (Ymax,Xmax) = self.screen.getmaxyx()
        if X > Xmax or X < 0:
            print "invalid conversion from x={} to X={} -> max={}".format(x,X,Xmax)
            self.exit()
        return X

    def Y(self,y):
        Y = int(self.y_origin + self.v_size - y)
        (Ymax,Xmax) = self.screen.getmaxyx()
        if Y > Ymax or Y < 0:
            print "invalid conversion from y={} to Y={} -> max={}".format(y,Y,Ymax)
            self.exit()
        return Y

    def convertCoord(self,x,y):
        return (self.X(x),self.Y(y))

    def convertCoordList(self,list_x, list_y):
        coord_list = zip(list_x,list_y)
        return [(self.X(x),self.Y(y)) for x,y in coord_list]

    def printXRange(self,min,max):
        mintime = time.strftime('%H:%M:%S',time.localtime(min))
        #mindate = datetime.datetime.fromtimestamp(int(min(absciss)))
        #mintime = mindate.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        self.screen.addstr(self.Y(-1),self.X(0),mintime)

        maxtime = time.strftime('%H:%M:%S',time.localtime(max))
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

    def getMaxLength():
        l = 0
        for core in self.data:
            if (l ==0 ):
                l = len(self.data[core])
            if (l!=0 and l!=len(self.data[core])):
                print "values have not same size: {} != {}".format(l,len(self.data[core]))
                self.exit()
        return l

    def drawConsole(self):
        import curses

        self.screen = curses.initscr()
        curses.start_color()
        self.consoleInit()

        (v_max,h_max) = self.screen.getmaxyx()

        self.screen.clear()
        self.screen.border('|','|','-','-','+','+','+','+')
        
        self.screen.addstr(self.Y(v_max),self.X(20),"PDCP throughput ({},{}) ".format(v_max,h_max))

        self.printAxes()
        self.printLegend('time','throughput in kbps')

        color = [curses.COLOR_BLUE,curses.COLOR_RED,curses.COLOR_GREEN,curses.COLOR_PURPLE,curses.COLOR_BLUE]
        curses.init_pair(1, color[1], curses.COLOR_BLACK)
        curses.init_pair(2, color[2], curses.COLOR_BLACK)
        curses.init_pair(3, color[3], curses.COLOR_BLACK)
        curses.init_pair(4, color[4], curses.COLOR_BLACK)
        
        self.getPdcpData()

        l = getMaxLength()
        sumordinate = [0] * l

        i=0

        # Calculate time to print in console
        import sys
        hmax = 0
        hmin = sys.maxint
        vmax=0
        vmin= sys.maxint
        for core in self.data:
            absciss = [ convertTimestampFromStringToTime(pair[0]) for pair in self.data[core] ] # timestamps
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


        colorIdx = 1
        for core in self.data:
            absciss = [ convertTimestampFromStringToTime(pair[0]) for pair in self.data[core] ] # time
            ordinate = [float(pair[1]) for pair in self.data[core]] # value to plot

            coord = zip(absciss,ordinate)
            for x,y in coord:
                xpos = int((x-min(absciss))/hstep)
                ypos = int((y-min(ordinate))/vstep)
                self.screen.addstr(self.Y(ypos),self.X(xpos),'+',curses.color_pair(colorIdx))
                
        # print sum
        sum = zip(absciss,sumordinate)
        for x,y in sum:
            xpos = int((x - min(absciss)) / hstep)
            ypos = int((y - min(sumordinate)) / vstep )
            self.screen.addstr(self.Y(ypos),self.X(xpos),'*')

        self.screen.refresh()
        self.screen.getch()

        #self.exit()
        curses.nocbreak()
        self.screen.keypad(0)
        curses.echo()
        curses.endwin()
