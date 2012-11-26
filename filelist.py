#encoding: UTF-8

import re
import os

import pygtk
pygtk.require('2.0')
import gobject


def natural_sort(l): 
   convert = lambda text: int(text) if text.isdigit() else text.lower() 
   alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
   return sorted(l, key=alphanum_key)


class FileList(gobject.GObject):
   def __init__(self):
      self.__gobject_init__()
      
      self.use_hidden_files = False
      self.cwd = ''
      self.lst = []  # [(fname, is_dir), ]

   def getCwd(self):
      return self.cwd

   def getCwdName(self):
      return os.path.split(self.cwd)[1]

   def __f_filter(self, fn, is_dir):
      #reads:  self.cwd, self.use_hidden_files
      if fn.startswith('.') and (not self.use_hidden_files):
         return False
      result = os.path.isdir(os.path.join(self.cwd, fn))
      if not is_dir:
         result = not result
      return result

   def loadCwdList(self):
      lst = os.listdir(self.cwd)
      lst_dirs = [(thefn,True) for thefn in \
            natural_sort( [fn for fn in lst if self.__f_filter(fn, True)] ) ]
      lst_files = [(thefn,False) for thefn in \
            natural_sort( [fn for fn in lst if self.__f_filter(fn, False)] ) ]
      self.lst = lst_dirs
      self.lst.extend( lst_files )

   def getItemFullPath(self, fn):
      return os.path.join(self.cwd, fn)
   
   def setUseHiddenFiles(self, val):
      self.use_hidden_files = val
      self.loadCwdList()
      self.emit('cwd-changed', self.cwd)
   
   def setCwd(self, pth):
      if not os.path.isdir(pth):
         print('FileList: not a directory: '+pth)
         return
         #raise ValueError, pth
      self.cwd = (pth.rstrip('/') if len(pth)>1 else pth)
      self.loadCwdList()
      self.emit('cwd-changed', self.cwd)

   def setCwdUp(self):
      self.setCwd( os.path.split(self.cwd)[0] )
   
   def setCwdInto(self, dirname):
      self.setCwd( os.path.join(self.cwd, dirname) )
   
   def setCwdHome(self):
      self.setCwd( os.path.expanduser('~') )
   

gobject.type_register(FileList)
gobject.signal_new('cwd-changed', FileList, gobject.SIGNAL_RUN_FIRST,
                   gobject.TYPE_NONE, (gobject.TYPE_STRING,))

