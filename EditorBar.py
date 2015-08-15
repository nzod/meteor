# encoding: UTF-8

import pygtk
pygtk.require('2.0')
import gtk
import glib


class EditorBar(gtk.EventBox):

    def __init__(self):
        gtk.EventBox.__init__(self)

        self.entry = gtk.Entry()

        box = gtk.HBox()
        box.pack_start(self.entry, expand=True, padding=2)
        self.add(box)
