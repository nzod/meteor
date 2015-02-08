#encoding: UTF-8

import os
import json


def obj_save(obj, fname):
   with open(fname, 'w') as f:
      json.dump(obj, f, indent=3, sort_keys=True)

def obj_load(fname):
   try:
      with open(fname, 'r') as f:
         obj = json.load(f)
         return obj
   except (IOError):
      return None


class Config:
   default = {
      'confirm-deletion': True,
      'remember-paths': False,
      'saved-paths': ['', ''],
      'opener-program': 'xdg-open',
      'pathbar-pos': 'top',
      'k-quit': 'C+q',
      'k-reload': 'C+r',
      'k-toggle-hidden': 'C+h',
      'k-nav-up': 'M+Up',
      'k-nav-home': 'M+Home',
      'k-file-rename': 'F2',
      'k-file-delete': 'C+k',
      'k-mark': 'm',
      'k-mark-all': 'M+m',
      'k-mark-section': 'C+m',
      'k-mark-inverse': 'CM+m'
     }
   
   def __init__(self, fname):
      self.o = {}
      self.fname = os.path.expanduser('~/.%s.json' % fname)
      if os.path.isfile(self.fname):
         self.o = obj_load(self.fname)
         if self.o is None:
            self.o = {}
      self.updateKeys()

   def updateKeys(self):
      defc = Config.default
      for ck in defc.iterkeys():
         if ck not in self.o:
            self.o[ck] = defc[ck]

   def __getitem__(self, k):
      return self.o[k]
      
   def __setitem__(self, k, v):
      self.o[k] = v

   def hasKey(self, k):
      return hasattr(self.o, k)
      
   def write(self):
      obj_save(self.o, self.fname)
      

conf = Config('meteor')
