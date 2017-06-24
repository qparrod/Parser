#!/usr/bin/python2.7

import curses
import time
import datetime

class Graph:
    def __init__(self):
        self.screen = curses.initscr()
        self.x_origin = 10
        self.y_origin = 2
        self.x_limit = 4
        self.y_limit = 5
        (v_max,h_max) = self.screen.getmaxyx()
        self.h_size = h_max-self.x_limit-self.x_origin-1
        self.v_size = v_max-self.y_limit-self.y_origin-1


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

    def drawBeautiful(self,data,data2,rlc,mac):
        import matplotlib.pyplot as plt
        import matplotlib.dates as dt

        self.exit()

        absciss  = [pair[1] for pair in data] # eg time
        ordinate = [pair[0] for pair in data] # value to plot

        t = [datetime.datetime.strptime(time.strftime('%H:%M:%S',time.localtime(int(i))),'%H:%M:%S') for i in absciss]
        dates = dt.date2num(t)

        plt.figure(1)
        plt.subplot(1,2,1)
        plt.plot_date(dates,ordinate, 'b-', label='LINUX-Disp_0 throughput in kbps')
        plt.title('PDCP throughput')
        absciss  = [pair[1] for pair in data2] # eg time
        ordinate2 = [pair[0] for pair in data2] # value to plot   
        plt.plot_date(dates,ordinate2, 'g-',label='LINUX-Disp_1 throughput in kbps')
        plt.xticks( rotation=25 )
        sumordinate = [ordinate[i]+ordinate2[i] for i in range(len(ordinate))]
        plt.plot_date(dates,sumordinate, 'r--',label='total throughput in kbps')
        plt.legend(bbox_to_anchor=(1.1, 1.05), shadow=True)

        plt.subplot(2,2,2)
        for core in rlc:
            absciss = [ pair[1] for pair in rlc[core] ]
            ordinate = [ time.mktime(pair[0].timetuple()) for pair in rlc[core] ]
            t = [datetime.datetime.strptime(time.strftime('%H:%M:%S',time.localtime(int(i))),'%H:%M:%S') for i in absciss]
            dates = dt.date2num(t)
            plt.plot_date(dates,ordinate, 'r--',label='core {} RLC throughput in kbps'.format(core))

        plt.show()

        #plt.plotfile('csv/throughput/MAC_throughput_FSP-1233.csv',(0,1),linestyle="",marker="o")
        #plt.show()



    def draw(self,data):
        print 'begin graph'
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