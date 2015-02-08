#encoding: UTF-8

import sys
import os

import pygtk
pygtk.require('2.0')
import gtk
import gobject

from config import conf
from filelist import FileList
from ShortkeyMixin import ShortkeyMixin
from FileViewPane import FileViewPane


class F:
   APP_NAME = 'meteor'
   APP_VER = '0.1'
   install_dir = ''
   
   filelists = [FileList(), FileList()]
   curr_flist = 0
   

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
      
      #-- resources
      F.install_dir = os.path.dirname( os.path.realpath(__file__) )
      ui_imgname = lambda s: os.path.join( F.conf['install-dir'], 'img', '%s.png'%s )
      
      #-- main widgets
      self.fviews = [FileViewPane(flist) for flist in F.filelists]
      
      #-- layout
      mainbox = gtk.HBox()
      mainbox.set_property('homogeneous', True)
      for fview in self.fviews:
         mainbox.pack_start(fview, expand=True, padding=0)

      self.add(mainbox)

      #-- hotkeys
      self.bind_shortkey(conf['k-quit'], self.onQuit)
      
      #-- set up fileviews
      for i,fview in enumerate(self.fviews):
         if conf['remember-paths'] and conf['saved-paths'][i]:
            F.filelists[i].setCwd( conf['saved-paths'][i] )
         else:
            F.filelists[i].setCwdHome()
         fview.fileview.connect('focus-in-event', self.onFviewFocusIn)
      self.fviews[0].setActive(True)
      
      #-- showtime
      self.show_all()
      
   def onQuit(self):
      for i,flist in enumerate(F.filelists):
         if conf['remember-paths']:
            conf['saved-paths'][i] = flist.getCwd()
         flist.teardown()
      
      conf.write()
      gtk.main_quit()
      
   def delete_event(self, widget, evt, data=None):
      self.onQuit()
      return False

   def onFviewFocusIn(self, evt_fview, evt):
      for fview in self.fviews:
         fview.setActive(False)
      evt_fview.getPane().setActive(True)
         
