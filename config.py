#encoding: UTF-8

import os

import po


class Config:
   def __init__(self, fname):
      self.o = {}
      self.fname = os.path.expanduser('~/.%s' % fname)
      self.loaded = False
      
      if os.path.isfile(self.fname):
         self.o = po.load(self.fname)
         self.loaded = True
         if self.o is None:
            self.o = {}
            self.loaded = False
      else:
         self.loaded = False  

   def __getitem__(self, k):
      return self.o[k]
      
   def __setitem__(self, k, v):
      self.o[k] = v

   def hasKey(self, k):
      return hasattr(self.o, k)
      
   def write(self):
      po.save(self.o, self.fname)
      

