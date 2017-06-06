#!/usr/bin/python2.7

import csv as c

class Csv:
    def __init__(self):
        self.filename = ''
        self.mode     = ''

    def open(self, name):
        self.filename = name
        self.mode     = 'w'

    def write(self, fields, data):
        with open(self.filename,self.mode) as csvfile:
            writer = c.DictWriter(csvfile,fieldnames=fields)
            writer.writeheader()
            for elements in data:
                writer.writerow(dict(zip(fields, elements)))