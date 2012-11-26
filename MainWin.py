#encoding: UTF-8

import sys
import os

import pygtk
pygtk.require('2.0')
import gtk
import gobject

from config import Config
from filelist import FileList
from ShortkeyMixin import ShortkeyMixin
from FileView import FileView


class F:
   APP_NAME = 'meteor'
   APP_VER = '0.1'
   conf = None
   filelist = FileList()
   

def confirm(text):
   dlg = gtk.MessageDialog(type=gtk.MESSAGE_QUESTION, buttons=gtk.BUTTONS_OK_CANCEL)
   dlg.set_markup(text)
   response = dlg.run()
   dlg.destroy()
   return (response==gtk.RESPONSE_OK)


class MainWin(gtk.Window, ShortkeyMixin):
   def __init__(self):
      gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
      ShortkeyMixin.__init__(self)
      
      self.set_title(F.APP_NAME)
      self.set_default_size(480, 460)
      self.connect('delete_event', self.delete_event)
      
      #-- Create and init configuration
      F.conf = Config(F.APP_NAME)
      if not F.conf.hasKey('install-dir'):
         F.conf['install-dir'] = os.path.dirname( os.path.realpath(__file__) )
      
      # == == ==  RESOURCES  == == ==
      
      ui_imgname = lambda s: os.path.join( F.conf['install-dir'], 'img', '%s.png'%s )
      # ....
      
      # == == ==  MAIN WIDGETS  == == ==
      self.fileview = FileView(F.filelist)
      fileview_container = gtk.ScrolledWindow()
      fileview_container.add(self.fileview)
      fileview_container.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
      #...
      
      # == == ==  LAYOUT  == == ==
      
      mainbox = gtk.VBox()
      mainbox.pack_start(fileview_container, expand=True, padding=0)

      self.add(mainbox)

      # == == ==  INIT UI & SYS  == == ==
      
      #-- Shortkeys...
      self.bind_shortkey('C+q', self.onQuit)
      
      #-- Set up ui
      F.filelist.setCwdHome()
      
      # == == ==  SHOW THE BABY  == == ==
      
      self.show_all()
      
      
   def onQuit(self):
      F.conf.write()
      
      gtk.main_quit()
      
      
   def delete_event(self, widget, evt, data=None):
      self.onQuit()
      return False
