#!/usr/bin/python2.7

from datetime import datetime, timedelta
import time

class Time:  

    def __init__(self,time=''):
        self.format = "%Y-%m-%dT%H:%M:%S.%fZ"
        self.time   = self.convertFromString(time)

    def convertFromString(self,string):
        if string != '' :
            return datetime.strptime(string, self.format)

    def convertTimestampFromStringToTime(self,timestamp):
        pattern = "%Y-%m-%d %H:%M:%S.%f"
        self.format = pattern
        # create a 9-tuple expressed time in local time
        return time.mktime(self.convertFromString(timestamp).timetuple())

    def convertLocalTime(self,val):
        pattern = '%H:%M:%S'
        t = time.strftime(pattern,time.localtime(int(val)))
        return datetime.strptime(t,pattern)

    #def __getattr__(self,attr):
    #    return self.time

    #def __setattr__(self,attr,val):
        
    def __add__(self,val):
        r = Time()
        r.time = self.time + timedelta(seconds=val)
        return r

    def __sub__(self,val):
        return self.time - timedelta(seconds=val)