# encoding: UTF-8

import pygtk
pygtk.require('2.0')
import gtk
import glib


class PathBar(gtk.EventBox):
    color_default = gtk.gdk.color_parse('#777')
    color_active = gtk.gdk.color_parse('#46718A')
    color_text = '#fff'

    def __init__(self, fview):
        gtk.EventBox.__init__(self)

        self.fview = fview

        self.lbl_path = gtk.Label()
        self.lbl_path.set_use_markup(True)
        self.lbl_path.set_single_line_mode(True)

        box = gtk.HBox()
        box.pack_start(self.lbl_path, expand=False, padding=4)
        self.add(box)

        self.setActive(False)

        self.fview.getFileList().connect('cwd-changed', self.onCwdChanged)

    def setActive(self, active):
        self.modify_bg(gtk.STATE_NORMAL,
                       PathBar.color_active if active else PathBar.color_default)

    def setPathLabel(self, pth):
        self.lbl_path.set_markup(
            '<span font_desc="9.0" foreground="%s">%s</span>'
            % (PathBar.color_text, glib.markup_escape_text(pth)))

    def onCwdChanged(self, srcobj, cwd):
        self.setPathLabel(cwd)
