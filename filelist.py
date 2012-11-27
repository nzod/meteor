#encoding: UTF-8

import re
import os

import pygtk
pygtk.require('2.0')
import gtk
import gobject

import pyinotify


class FsEvtHandler(pyinotify.ProcessEvent):
   def process_IN_CREATE(self, event):
      self.flist_inst.onFileCreated(event.pathname)

   def process_IN_DELETE(self, event):
      self.flist_inst.onFileDeleted(event.pathname)


def natural_sort(l): 
   convert = lambda text: int(text) if text.isdigit() else text.lower() 
   alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
   return sorted(l, key=alphanum_key)


class FileList(gtk.ListStore):
   def __init__(self):
      gtk.ListStore.__init__(self, bool, str, str)  # is_dir, fname, fname_markup
      
      self.use_hidden_files = False
      self.cwd = ''
      
      self.name_markup_fun = None #assigned later by owner list
      
      self.watch_mgr = pyinotify.WatchManager()
      evt_handler = FsEvtHandler()
      evt_handler.flist_inst = self
      self.watch_notifier = pyinotify.ThreadedNotifier(self.watch_mgr, evt_handler)
      self.watch_dd = None
      self.watch_notifier.start()

   def teardown(self):
      self.watch_notifier.stop()

   def getCwd(self):
      return self.cwd

   def getCwdName(self):
      return os.path.split(self.cwd)[1]

   def hasFilename(self, fname):
      return (fname in os.listdir(self.cwd))

   def findItemByFname(self, fname):
      for i,row in enumerate(self):
         if row[1]==fname:
            return i

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
      lst_dirs = natural_sort( [fn for fn in lst if self.__f_filter(fn, True)] )
      lst_files = natural_sort( [fn for fn in lst if self.__f_filter(fn, False)] )
      
      self.clear()
      for fname in lst_dirs:
         self.append(( True, fname, self.fname_markup_fun(fname, True) ))
      for fname in lst_files:
         self.append(( False, fname, self.fname_markup_fun(fname, False) ))
      
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
      cwd = (pth.rstrip('/') if len(pth)>1 else pth)
      if cwd != self.cwd:
         self.endWatch()
         self.beginWatch(cwd)
      self.cwd = cwd
      self.loadCwdList()
      self.emit('cwd-changed', self.cwd)

   def setCwdUp(self):
      self.setCwd( os.path.split(self.cwd)[0] )
   
   def setCwdInto(self, dirname):
      self.setCwd( os.path.join(self.cwd, dirname) )
   
   def setCwdHome(self):
      self.setCwd( os.path.expanduser('~') )
   
   
   def beginWatch(self, pth):
      self.watch_dd = self.watch_mgr.add_watch(pth,
            pyinotify.IN_DELETE|pyinotify.IN_CREATE, rec=False)
   
   def endWatch(self):
      if self.watch_dd is not None:
         self.watch_mgr.rm_watch(self.watch_dd.values())
         self.watch_dd = None
   
   def onFileCreated(self, fname):
      is_dir = os.path.isdir(fname)
      self.emit('file-created', fname)
      
   def onFileDeleted(self, pth):
      _,fname = os.path.split(pth)
      for row in self:
         if row[1]==fname:
            self.remove(row.iter)
            break
      self.emit('file-deleted', fname)
   

gobject.type_register(FileList)
gobject.signal_new('cwd-changed', FileList, gobject.SIGNAL_RUN_FIRST,
                   gobject.TYPE_NONE, (gobject.TYPE_STRING,))
gobject.signal_new('file-created', FileList, gobject.SIGNAL_RUN_FIRST,
                   gobject.TYPE_NONE, (gobject.TYPE_STRING,))
gobject.signal_new('file-deleted', FileList, gobject.SIGNAL_RUN_FIRST,
                   gobject.TYPE_NONE, (gobject.TYPE_STRING,))
