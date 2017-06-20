import curses
import time

def draw(data):
    print 'begin graph'
    # begin curses application
    screen = curses.initscr()
    (v_max,h_max) = screen.getmaxyx()
    x_origin = 10
    x_limit = 4
    y_origin = 2
    y_limit = 5


    v_box = 10
    h_box = h_max
    scr_boxes = []
    v_box_origin = 0
    h_box_origin = 0
    box_space = 0

    #while(v_box_origin+v_box<v_max):
    #    scr = curses.newwin(v_box,h_box,v_box_origin,h_box_origin)
    #    scr.border('|','|','_','_','|','|','|','|')
    #    scr_boxes.append(scr)
    #    v_box_origin += v_box + box_space -1
    # 
    # for scr in scr_boxes:
    #   scr.refresh()
    #scr_boxes[-1].getch()

    screen.clear()
    screen.border('|','|','-','-','+','+','+','+')
    h_size = h_max-x_limit-x_origin-1
    v_size = v_max-y_limit-y_origin-1
    screen.addstr(1,20,"Trace throughput ({},{}) ".format(v_max,h_max))
    screen.addstr(y_origin,x_origin,'^')
    screen.vline(y_origin+1,x_origin,'|',v_size)
    screen.addstr(y_origin+v_size,x_origin,'|')
    screen.hline(y_origin+v_size,x_origin+1,'_',h_size)
    screen.addstr(y_origin+v_size,x_origin+h_size,'>')
    hlegend='time'
    vlegend='throughput in kbps'
    screen.addstr(y_origin+v_size+2,int(0.5*(x_origin+h_size-len(hlegend))),hlegend)
    screen.addstr(y_origin+1,x_origin+2,vlegend)

    absciss  = [pair[1] for pair in data] # eg time
    ordinate = [pair[0] for pair in data] # value to plot
    vstep = float((max(ordinate)-min(ordinate))/v_size)
    hstep = float((max(absciss)-min(absciss))/h_size)

    screen.addstr(y_origin,x_origin-len(str(int(max(ordinate))))-1,str(int(max(ordinate))))
    screen.addstr(y_origin+v_size,x_origin-len(str(int(min(ordinate))))-1,str(int(min(ordinate))))

    mintime = time.strftime('%H:%M:%S',time.localtime(int(min(absciss))))
    screen.addstr(y_origin+v_size+1,x_origin,mintime)
    maxtime = time.strftime('%H:%M:%S',time.localtime(int(max(absciss))))
    screen.addstr(y_origin+v_size+1,x_origin+h_size-len(maxtime),maxtime)

    xpos = 0    
    ypos = 0
    for (e,t) in data:
        #xpos=xpos+1
        xpos = int((t - min(absciss)) / hstep)
        ypos = int((e - min(ordinate)) / vstep )

        if (y_origin+v_size-ypos < v_max and x_origin+xpos < h_max):
            screen.addstr(y_origin+v_size-ypos,x_origin+xpos,'+')
        else:
            screen.refresh()
            screen.getch()
            curses.nocbreak(); screen.keypad(0); curses.echo(); curses.endwin()
            print "ypos={};xpos={}  max=({};{})".format(ypos,xpos,v_max,h_max)
            print v_max
            print y_origin+v_size-ypos
            print h_max
            print x_origin+xpos
            print "error exit"
            exit()

    screen.refresh()
    screen.getch()

    # terminating curses application
    curses.nocbreak(); screen.keypad(0); curses.echo(); curses.endwin()
    print 'end graph'
    print "hstep={} vstep={}".format(hstep,vstep)