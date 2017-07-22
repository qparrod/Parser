#!/usr/bin/python2.7

import csv
#import csv as c

class Csv:
    def __init__(self):
        self.filename = ''
        self.mode     = ''

        '''
    def open(self, name):
        self.filename = name
        self.mode     = 'w'

    def write(self, fields, data):
        with open(self.filename,self.mode) as csvfile:
            writer = c.DictWriter(csvfile,fieldnames=fields)
            writer.writeheader()
            for elements in data:
                writer.writerow(dict(zip(fields, elements)))
                '''

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

            if settings.cloud and 'PDCP' in name and 'FSP-' in core:
                if settings.verbose : print "filter PDCP FSP core {}".format(core)
                continue

            if 'MAC' in name or 'UL_RLC' in name:
                # special case where uegroup in present in data...
                # this information is no everywhere in traces...
                ueGroupToFilter = filtering(data[core])
                ueGroups=[]

                for (timestamp,ueGroup,throughput) in data[core]:
                    if(ueGroup in ueGroupToFilter):
                        continue
                    line = (timestamp,throughput)
                    fd = 0 
                    if ueGroup not in ueGroups:
                        ueGroups.append(ueGroup)
                        fd = open('csv/{}/{}_{}_{}_ueGroup{}.csv'.format(directory,name,type,core,ueGroup),'w')
                        writer = csv.writer(fd)
                        writer.writerow(header)
                    else:
                        fd = open('csv/{}/{}_{}_{}_ueGroup{}.csv'.format(directory,name,type,core,ueGroup),'a')
                        writer = csv.writer(fd)
                    writer.writerow(line)
                    fd.close()
            else:
                if (all(e[1]<0.1 for e in data[core]) ):
                    if settings.verbose: print "{}: data always 0.0 for core {} -> filtered".format(name,core)
                    continue
                fd = open('csv/{}/{}_{}_{}.csv'.format(directory,name,type,core),'w')
                writer = csv.writer(fd)
                writer.writerow(header)
                for line in data[core]:
                    writer.writerow(line)
                fd.close()
        if settings.verbose : print "CSV file created for {} {}".format(name,type)

    def createCsvThroughput(self,layerName,data):
        self.createCsv(layerName,'throughput',data)

    def createCsvLoad(self,data):
        self.createCsv('CPU','load',data)