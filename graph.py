#!/usr/bin/python2.7

import curses
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


    def printAxes(self):
        self.screen.addstr(self.y_origin,self.x_origin,'^')
        self.screen.vline(self.y_origin+1,self.x_origin,'|',self.v_size)
        self.screen.addstr(self.y_origin+self.v_size,self.x_origin,'|')
        self.screen.hline(self.y_origin+self.v_size,self.x_origin+1,'_',self.h_size)
        self.screen.addstr(self.y_origin+self.v_size,self.x_origin+self.h_size,'>')

    def printLegend(self,xlegend,ylegend):
        self.screen.addstr(self.y_origin+self.v_size+2,int(0.5*(self.x_origin+self.h_size-len(xlegend))),xlegend)
        self.screen.addstr(self.y_origin+1,self.x_origin+2,ylegend)

    def exit(self):
        # terminating curses application
        curses.nocbreak(); self.screen.keypad(0); curses.echo(); curses.endwin()


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


    def drawConsole(self,data):
        print 'begin graph'

        self.screen = curses.initscr()

        self.x_origin = 10
        self.y_origin = 2
        self.x_limit = 4
        self.y_limit = 5
        (v_max,h_max) = self.screen.getmaxyx()
        self.h_size = h_max-self.x_limit-self.x_origin-1
        self.v_size = v_max-self.y_limit-self.y_origin-1


        # begin curses application
        (v_max,h_max) = self.screen.getmaxyx()

        self.screen.clear()
        self.screen.border('|','|','-','-','+','+','+','+')
        
        self.screen.addstr(1,20,"Trace throughput ({},{}) ".format(v_max,h_max))

        self.printAxes()
        self.printLegend('time','throughput in kbps')
        
        absciss  = [pair[1] for pair in data] # eg time
        ordinate = [pair[0] for pair in data] # value to plot
        vstep = float((max(ordinate)-min(ordinate))/self.v_size)
        hstep = float((max(absciss)-min(absciss))/self.h_size)

        self.screen.addstr(self.y_origin,self.x_origin-len(str(int(max(ordinate))))-1,str(int(max(ordinate))))
        self.screen.addstr(self.y_origin+self.v_size,self.x_origin-len(str(int(min(ordinate))))-1,str(int(min(ordinate))))

        mintime = time.strftime('%H:%M:%S',time.localtime(int(min(absciss))))
        mindate = datetime.datetime.fromtimestamp(int(min(absciss)))
        mintime = mindate.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        self.screen.addstr(self.y_origin+self.v_size+1,self.x_origin,mintime)
        maxtime = time.strftime('%H:%M:%S',time.localtime(int(max(absciss))))
        self.screen.addstr(self.y_origin+self.v_size+1,self.x_origin+self.h_size-len(maxtime),maxtime)

        xpos = 0    
        ypos = 0
        for (e,t) in data:
            #xpos=xpos+1
            xpos = int((t - min(absciss)) / hstep)
            ypos = int((e - min(ordinate)) / vstep )

            if (self.y_origin+self.v_size-ypos < v_max and self.x_origin+xpos < h_max):
                self.screen.addstr(self.y_origin+self.v_size-ypos,self.x_origin+xpos,'+')
            else:
                self.screen.refresh()
                self.screen.getch()
                self.exit()
                print "ypos={};xpos={}  max=({};{})".format(ypos,xpos,v_max,self.h_max)
                print v_max
                print self.y_origin+self.v_size-ypos
                print h_max
                print self.x_origin+xpos
                print "error exit"
                exit()

        self.screen.refresh()
        self.screen.getch()

        self.exit()
        print 'end graph'
        print "hstep={} vstep={}".format(hstep,vstep)