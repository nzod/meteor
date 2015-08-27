# encoding: UTF-8

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


class MainWin(gtk.Window, ShortkeyMixin):

    def __init__(self):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        ShortkeyMixin.__init__(self)

        self.set_title('zfm')
        self.set_default_size(360, 460)
        self.connect('delete_event', self.delete_event)

        #-- main widgets
        self.filelists = [FileList(), FileList()]
        self.filelists[0].setOtherFlist(self.filelists[1])
        self.filelists[1].setOtherFlist(self.filelists[0])
        self.fviews = [FileViewPane(flist) for flist in self.filelists]

        #-- layout
        mainbox = gtk.HBox()
        mainbox.set_property('homogeneous', True)
        for fview in self.fviews:
            mainbox.pack_start(fview, expand=True, padding=0)

        self.add(mainbox)

        #-- hotkeys
        self.bind_shortkey(conf['k-quit'], self.onQuit)

        #-- set up fileviews
        for i, fview in enumerate(self.fviews):
            if conf['remember-paths'] and len(conf['saved-paths']) >= i + 1:
                self.filelists[i].setCwd(conf['saved-paths'][i])
            else:
                self.filelists[i].setCwdHome()
            fview.fileview.connect('focus-in-event', self.onFviewFocusIn)
        self.fviews[0].setActive(True)

        #-- restore geom
        if conf['remember-wingeom'] and conf['wingeom'] is not None:
            geom = conf['wingeom']
            self.move(geom[0], geom[1])
            self.resize(geom[2], geom[3])

        #-- showtime
        self.show_all()

    def onQuit(self):
        saved_paths = []
        for i, flist in enumerate(self.filelists):
            saved_paths.append(flist.getCwd())
            flist.teardown()
        if conf['remember-paths']:
            conf['saved-paths'] = saved_paths
        if conf['remember-wingeom']:
            x, y = self.get_position()
            w, h = self.get_size()
            conf['wingeom'] = [x, y, w, h]

        conf.write()
        gtk.main_quit()

    def delete_event(self, widget, evt, data=None):
        self.onQuit()
        return False

    def onFviewFocusIn(self, evt_fview, evt):
        for fview in self.fviews:
            fview.setActive(False)
        evt_fview.getPane().setActive(True)
