def init():
    global files
    global png
    global dpi
    global plot
    global verbose
    global branch
    global clear
    global board
    global deployment
    global application
    global cloud
    global console
    global graphAllowed
    global programName
    global syslogType
    global workPathNeeded
    global path
    global SUTCores
    global GTPCores
    global fileFilter


    # program default values
    files          = []
    png            = False
    verbose        = False
    dpi            = 50
    plot           = False
    cloud          = False
    clear          = False
    console        = False
    graphAllowed   = False
    workPathNeeded = False
    path           = ''
    branch         = ''
    programName    = 'parser.py'
    board          = 'fsm3'
    deployment     = '6DSP'
    application    = 'syslogAnalyzer'
    syslogType     = 'udplog'

    fileFilter = [ 'FSM3_RAP_reset', 'GTP_address_configuration', 'LteL2AddressConfig', 'Node_startup', 'syscomroute' ]

    SUTCores = { '6DSP' : { 'DL' : ['FSP-1231','FSP-1232','FSP-1233','FSP-1234'], 'UL' : ['FSP-1242','FSP-1243'] },
                 'cBTS 6DSP' : { 'DL' : ['LINUX-Disp_0','LINUX-Disp_1','FSP-1231','FSP-1232','FSP-1233','FSP-1234'], 'UL' : ['LINUX-Disp_0','LINUX-Disp_1','FSP-1242','FSP-1243'] }
               }

    GTPCores = { 'cBTS 6DSP' : {'DL' : ['LINUX-Disp_2'] , 'UL' : ['FSP-1264'] } }


class Color:
    ok         = '\033[92m'
    error      = '\033[91m'
    warning    = '\033[93m'
    underline  = '\033[4m'
    bold       = '\033[1m'
    nocolor    = '\033[0m'


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

        out = '\r{0} {1} {2:>3}%\033[0m [{3}{4}] time: {5:}:{6:02d}:{7:02d}.{8:03d}'.format(self.title,color,perc,'='*bar,' ' * (self.maxbar - bar),time.seconds//3600,(time.seconds//60)%60,time.seconds,time.microseconds/1000) 

        sys.stdout.write(out)

        sys.stdout.flush()
