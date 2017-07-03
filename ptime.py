#!/usr/bin/python2.7

from datetime import datetime, timedelta
import time

class Time:  

    def __init__(self,time='',format='%Y-%m-%dT%H:%M:%S.%fZ'):
        self.format    = format
        self.time      = self.convertFromString(time)

    def convertFromString(self,string):
        if string != '' :
            return datetime.strptime(string, self.format)

    def convertTimestampFromStringToTime(self,timestamp):
        # create a 9-tuple expressed time in local time
        return time.mktime(self.convertFromString(timestamp).timetuple())

    def convertLocalTime(self,val):
        t = convertLocalTimeToTime(val)
        return datetime.strptime(t,self.format)

    def convertLocalTimeToTime(self,val):
        return time.strftime(self.format,time.localtime(val))
        
    def __add__(self,val):
        return self.time + timedelta(seconds=val)

    def __sub__(self,val):
        return self.time - timedelta(seconds=val)