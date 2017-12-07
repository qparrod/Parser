#!/usr/bin/python2.7

import csv
#import csv as c

class Csv:
    def __init__(self):
        self.filename = ''
        self.mode     = ''

    def createCsv(self,name,type,data):
        import settings
        from settings import *
        if data == {}:
            if settings.verbose : print Color.warning + "no data collected for {} {}".format(name,type) + Color.nocolor
            return

        for core in data:
            directory = ''
            header= []
            if type=="throughput" :
                directory = 'throughput'
                header = ['timestamp','{} {} in kbps for core {}'.format(name,type,core)]
            elif type=="load" :
                directory = 'cpuload'
                header = ['timestamp','{} {} in % for core {}'.format(name,type,core)]
            elif type == 'discard' :
                directory = 'discard'
                header = ['timestamp','{} {} for core {}'.format(name,type,core)]
            else:
                print "csv file type not recognized"
                exit()


            fd = open('csv/{}/{}_{}_{}.csv'.format(directory,name,type,core),'w')
            writer = csv.writer(fd)
            writer.writerow(header)
            for line in data[core]:
                writer.writerow(line)
            fd.close()
            if settings.verbose : print "CSV file created for {} {} (csv/{}/{}_{}_{}.csv)".format(name,type,directory,name,type,core)

    def createCsvThroughput(self,layerName,data):
        self.createCsv(layerName,'throughput',data)

    def createCsvLoad(self,data):
        self.createCsv('CPU','load',data)