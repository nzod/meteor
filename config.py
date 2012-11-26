#encoding: UTF-8

import os
import json


def obj_save(obj, fname):
   with open(fname, 'w') as f:
      json.dump(obj, f, indent=3)

def obj_load(fname):
   try:
      with open(fname, 'r') as f:
         obj = json.load(f)
         return obj
   except (IOError):
      return None


class Config:
   default = { "opener_program": "gnome-open", 
               "pathbar": {
                  "position": "top"
               }
             }
   
   def __init__(self, fname):
      self.o = {}
      self.fname = os.path.expanduser('~/.%s' % fname)
      
      if os.path.isfile(self.fname):
         self.o = obj_load(self.fname)
         if self.o is None:
            self.o = Config.default
      else:
         self.o = Config.default

   def __getitem__(self, k):
      return self.o[k]
      
   def __setitem__(self, k, v):
      self.o[k] = v

   def hasKey(self, k):
      return hasattr(self.o, k)
      
   def write(self):
      obj_save(self.o, self.fname)
      

conf = Config('meteor')
