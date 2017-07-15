def init():
    global files
    global png
    global dpi
    global showgraph
    global verbose
    global clear
    files = []
    png = False
    verbose = False
    dpi = 50
    showgraph = False
    clear = False


class Color:
    ok       = '\033[92m'
    error    = '\033[91m'
    warning  = '\033[93m'
    bold     = '\033[1m'
    nocolor  = '\033[0m'


class ProgressBar:
    def __init__ (self, valmax, maxbar, title):
        if valmax == 0:  valmax = 1
        if maxbar > 200: maxbar = 200
        self.valmax = valmax
        self.maxbar = maxbar
        self.title  = title
    
    def update(self, val, time):
        import sys
        perc  = int(round((float(val) / float(self.valmax)) * 100))
        scale = 100.0 / float(self.maxbar)
        bar   = int(perc / scale)
 
        color = ''

        if (perc!=100): color = Color.nocolor
        else:           color = Color.ok

        out = '\r{0} {1} {2:>3}%\033[0m [{3}{4}] time: {5:}:{6:02d}:{7:02d}.{8:03d}'.format(self.title,color,perc,'='*bar,' ' * (self.maxbar - bar),
            time.seconds//3600,(time.seconds//60)%60,time.seconds,time.microseconds/1000) 

        sys.stdout.write(out)

        if perc == 100 : sys.stdout.write('\n')
        sys.stdout.flush()
