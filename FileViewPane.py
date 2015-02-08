#encoding: UTF-8

import pygtk
pygtk.require('2.0')
import gtk

from FileView import FileView
from PathBar import PathBar



class FileViewPane(gtk.EventBox):
   def __init__(self, flist):
      gtk.EventBox.__init__(self)
      
      self.fileview = FileView(flist, self)
      fileview_container = gtk.ScrolledWindow()
      fileview_container.add(self.fileview)
      fileview_container.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
      
      self.pathbar = PathBar(self.fileview)
      
      box = gtk.VBox()
      box.pack_start(self.pathbar, expand=False)
      box.pack_start(fileview_container, expand=True)
      self.add(box)
   
   def setActive(self, active):
      self.pathbar.setActive(active)
      self.fileview.setActive(active)
