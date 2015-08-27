# encoding: UTF-8


class PairedItem(object):
    
    def __init__(self, other=None):
        self.other = other
    
    def getOther(self):
        return self.other
    
    def setOther(self, other):
        self.other = other
        