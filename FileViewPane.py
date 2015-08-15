# encoding: UTF-8

import pygtk
pygtk.require('2.0')
import gtk

from FileView import FileView
from PathBar import PathBar
from EditorBar import EditorBar


class FileViewPane(gtk.EventBox):

    def __init__(self, flist):
        gtk.EventBox.__init__(self)

        self.fileview = FileView(flist, self)
        fileview_container = gtk.ScrolledWindow()
        fileview_container.add(self.fileview)
        fileview_container.set_policy(
            gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        self.pathbar = PathBar(self.fileview)
        self.editorbar = EditorBar()

        self.box = gtk.VBox()
        self.box.pack_start(self.pathbar, expand=False)
        self.box.pack_start(fileview_container, expand=True)
        # self.box.pack_start(self.editorbar, expand=False)
        self.add(self.box)

    def setActive(self, active):
        self.pathbar.setActive(active)
        self.fileview.setActive(active)

    def showEditor(self):
        self.box.pack_end(self.editorbar, expand=False)

    def hideEditor(self):
        self.box.remove(self.editorbar)
